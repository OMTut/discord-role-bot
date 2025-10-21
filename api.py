"""
FastAPI server for Discord Role Bot
Provides REST endpoints to access bot data
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI(
    title="Discord Role Bot API",
    description="REST API for accessing Discord roles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Will be set by main bot
bot_instance = None


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    if not bot_instance:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    if not bot_instance.user:
        raise HTTPException(status_code=503, detail="Bot not connected to Discord")
    return {"status": "healthy", "bot": bot_instance.user.name}


@app.get("/api/roles", response_model=List[Dict[str, Any]], tags=["Roles"])
async def get_roles():
    """Get all available roles from the configured guild"""
    if not bot_instance:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    from config import config
    from utils.roles import get_guild_roles
    
    guild = bot_instance.get_guild(config.guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    roles = get_guild_roles(guild)
    return roles


def run_api(host: str = "0.0.0.0", port: int = 8001):
    """Start the FastAPI server"""
    uvicorn.run(app, host=host, port=port, log_level="info")
