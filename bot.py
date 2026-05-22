import discord
import httpx
from discord.ext import commands
from config import config
from utils.roles import get_guild_roles
from threading import Thread
from api import app, run_api

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
    
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print(f'Environment: {config.ENVIRONMENT}')
    print('=' * 50)
    
    # Get the configured guild
    guild = bot.get_guild(config.guild_id)
    if not guild:
        print(f'Error: Could not find guild with ID: {config.guild_id}')
        return
    
    try:
        # Fetch roles using utility function
        roles = get_guild_roles(guild)
        
        print(f'✅ Connected to guild: {guild.name} (ID: {guild.id})')
        print(f'✅ Guild members: {guild.member_count}')
        print(f'✅ Found {len(roles)} available roles:')
        print('-' * 30)
        
        # Display roles
        if roles:
            for role in roles:
                print(f'  • {role["name"]} (ID: {role["id"]})')
        else:
            print('  No roles found (only managed roles or @everyone exist)')
            
        print('-' * 30)
        print(f'🚀 {bot.user.name} is ready and running!')
        
    except Exception as e:
        print(f'Error fetching guild information: {e}')
        print('Check your bot permissions and guild configuration')


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
                print(f"✅ Synced roles for {after.name} ({after.id})")
            else:
                print(f"⚠️  Failed to sync roles for {after.name}: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error syncing roles for {after.name}: {e}")


def main():
    try:
        # Validate configuration before starting
        config.validate()
        
        print('Starting Discord Role Bot...')
        print(f'Environment: {config.ENVIRONMENT}')
        print(f'Target Guild ID: {config.guild_id}')
        print('=' * 50)
        
        # Start the FastAPI server in a background thread
        api_thread = Thread(target=run_api, daemon=True)
        api_thread.start()
        print('FastAPI server started on http://0.0.0.0:8001')
        print('=' * 50)
        
        # Start the bot
        bot.run(config.DISCORD_TOKEN)
        
    except ValueError as e:
        print(f'Configuration error: {e}')
        print('Please check your .env file and ensure all required values are set')
        return 1
    except Exception as e:
        print(f'Unexpected error: {e}')
        return 1


if __name__ == "__main__":
    exit(main())
