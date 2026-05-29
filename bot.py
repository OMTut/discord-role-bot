import discord
import httpx
import logging
import logging.handlers
import os
from discord.ext import commands
from config import config
from utils.roles import get_guild_roles
from threading import Thread
from api import app, run_api


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        filename="logs/gibbs.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=[stream_handler, file_handler])


logger = logging.getLogger("gibbs")

#########################################
# Create Bot Instance
# Returns: Configured Discord bot instance
#########################################
def create_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    bot = commands.Bot(
        command_prefix=config.COMMAND_PREFIX,
        intents=intents,
        description="Discord Role Management Bot"
    )
    return bot


# Create bot instance
bot = create_bot()


#########################################
# Bot Event Handler
# on_ready
# This event is triggered when the bot has successfully connected to Discord
#########################################
@bot.event
async def on_ready():
    from api import bot_instance as set_bot_instance, bot_instance
    import api
    api.bot_instance = bot
    
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Environment: {config.ENVIRONMENT}')

    # Get the configured guild
    guild = bot.get_guild(config.guild_id)
    if not guild:
        logger.error(f'Could not find guild with ID: {config.guild_id}')
        return

    try:
        # Fetch roles using utility function
        roles = get_guild_roles(guild)

        logger.info(f'Connected to guild: {guild.name} (ID: {guild.id})')
        logger.info(f'Guild members: {guild.member_count}')
        if roles:
            role_list = ", ".join(f'{r["name"]} ({r["id"]})' for r in roles)
            logger.info(f'Found {len(roles)} available roles: {role_list}')
        else:
            logger.info('No roles found (only managed roles or @everyone exist)')

        logger.info(f'{bot.user.name} is ready and running!')

    except Exception as e:
        logger.error(f'Error fetching guild information: {e}')
        logger.error('Check your bot permissions and guild configuration')


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Fires when a member's roles change in Discord — pushes update to Naja Admin."""
    if before.roles == after.roles:
        return

    role_discord_ids = [str(role.id) for role in after.roles if role.name != "@everyone"]
    all_guild_role_ids = [str(role.id) for role in after.guild.roles if role.name != "@everyone" and not role.managed]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.NAJA_ADMIN_URL}/api/bot/sync-roles",
                json={
                    "discord_id": str(after.id),
                    "role_discord_ids": role_discord_ids,
                    "all_guild_role_ids": all_guild_role_ids,
                },
                headers={"X-API-Key": config.BOT_API_KEY},
                timeout=10.0,
            )
            if response.status_code == 200:
                logger.info(f"Synced roles for {after.name} ({after.id})")
            else:
                logger.warning(f"Failed to sync roles for {after.name}: HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"Error syncing roles for {after.name}: {e}")


def main():
    try:
        setup_logging()
        # Validate configuration before starting
        config.validate()
        
        logger.info('Starting Discord Role Bot...')
        logger.info(f'Environment: {config.ENVIRONMENT}')
        logger.info(f'Target Guild ID: {config.guild_id}')

        # Start the FastAPI server in a background thread
        api_thread = Thread(target=run_api, daemon=True)
        api_thread.start()
        logger.info(f'FastAPI server started on http://{config.API_HOST}:{config.API_PORT}')

        # Start the bot
        bot.run(config.DISCORD_TOKEN)

    except ValueError as e:
        logger.error(f'Configuration error: {e}')
        logger.error('Please check your .env file and ensure all required values are set')
        return 1
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return 1


if __name__ == "__main__":
    exit(main())
