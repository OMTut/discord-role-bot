import discord
from discord.ext import commands
from config import config
from utils.roles import get_guild_roles

#########################################
# Create Bot Instance
# Returns: Configured Discord bot instance
#########################################
def create_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.guilds = True
    
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


def main():
    try:
        # Validate configuration before starting
        config.validate()
        
        print('Starting Discord Role Bot...')
        print(f'Environment: {config.ENVIRONMENT}')
        print(f'Target Guild ID: {config.guild_id}')
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
