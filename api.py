"""
FastAPI server for Discord Role Bot
Provides REST endpoints to access bot data
"""
import asyncio
import hmac
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(
    title="Discord Role Bot API",
    description="REST API for accessing Discord roles",
    version="1.0.0"
)

# CORS is restricted to Naja Admin only — this API is internal
allowed_origins = os.getenv("NAJA_ADMIN_URL", "http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins],
    allow_credentials=True,
    allow_methods=["GET", "PUT"],
    allow_headers=["X-API-Key", "Content-Type"],
)

# Will be set by main bot
bot_instance = None


def _check_api_key(x_api_key: str):
    from config import config
    if not config.BOT_API_KEY or not hmac.compare_digest(x_api_key, config.BOT_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


def _validate_discord_id(discord_id: str) -> int:
    if not discord_id.isdigit():
        raise HTTPException(status_code=422, detail="Invalid Discord user ID format")
    return int(discord_id)


@app.get("/health", tags=["Health"])
async def health_check(x_api_key: str = Header(...)):
    """Health check endpoint"""
    _check_api_key(x_api_key)
    if not bot_instance:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    if not bot_instance.user:
        raise HTTPException(status_code=503, detail="Bot not connected to Discord")
    return {"status": "healthy"}


@app.get("/api/roles", response_model=List[Dict[str, Any]], tags=["Roles"])
async def get_roles(x_api_key: str = Header(...)):
    """Get all available roles from the configured guild"""
    _check_api_key(x_api_key)

    if not bot_instance:
        raise HTTPException(status_code=503, detail="Bot not initialized")

    from config import config
    from utils.roles import get_guild_roles

    guild = bot_instance.get_guild(config.guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    roles = get_guild_roles(guild)
    return roles


class SetRolesRequest(BaseModel):
    assigned_role_discord_ids: List[str]
    managed_role_discord_ids: List[str]


@app.put("/api/members/{discord_user_id}/roles", tags=["Members"])
async def set_member_roles(
    discord_user_id: str,
    body: SetRolesRequest,
    x_api_key: str = Header(...),
):
    """Set a member's Discord roles. Only touches roles managed by Naja Admin."""
    _check_api_key(x_api_key)
    _validate_discord_id(discord_user_id)

    if not bot_instance:
        raise HTTPException(status_code=503, detail="Bot not initialized")

    from config import config
    from utils.roles import set_member_roles as _set_member_roles

    guild = bot_instance.get_guild(config.guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    # Schedule on the bot's event loop — Discord.py operations must run there
    future = asyncio.run_coroutine_threadsafe(
        _set_member_roles(
            guild,
            discord_user_id,
            body.assigned_role_discord_ids,
            body.managed_role_discord_ids,
        ),
        bot_instance.loop,
    )
    final_role_ids, not_in_discord_ids, errors = await asyncio.wrap_future(future)
    return {
        "applied_role_discord_ids": final_role_ids,
        "not_in_discord_ids": not_in_discord_ids,
        "errors": errors,
    }


def run_api(host: str = "0.0.0.0", port: int = 8001):
    """Start the FastAPI server"""
    uvicorn.run(app, host=host, port=port, log_level="info")
