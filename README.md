# Discord Role Bot

A Discord bot designed to interact with Discord servers and manage role information. This bot can connect to different Discord servers based on environment configuration and provides role listing functionality.

## Features

- **Multi-Environment Support**: Separate configurations for development and production servers
- **Role Management**: Lists all non-managed roles (excluding bot roles and @everyone)
- **REST API**: FastAPI endpoints to fetch roles programmatically

## Setup

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token (from Discord Developer Portal)
- Discord Server ID(s) where the bot will operate

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd discord-role-bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual values
   ```

### Environment Configuration

Edit the `.env` file with your actual Discord bot credentials.

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token to your `.env` file
4. Enable the following bot permissions:
   - View Channels
   - Read Message History
   - Send Messages
5. Add the bot to your Discord server(s)

## Usage

### Running the Bot

```bash
python bot.py
```

The bot will:
1. Connect to Discord using your token
2. Join the appropriate server based on your `ENVIRONMENT` setting
3. Print connection status and list all available roles

### Environment Modes

- **Development** (`ENVIRONMENT=development`): Uses `DEV_GUILD_ID`
- **Production** (`ENVIRONMENT=production`): Uses `PROD_GUILD_ID`

## API Endpoints

The bot exposes a FastAPI server on port `8001` with the following endpoints:

- /health - get connection status
- /api/roles - get all available roles from the org
- /api/members/{discord-user-id}/roles - get roles of a user
- /api/members/{discord-user-id}/roles - put (set) user's role


## Dependencies

- `discord.py>=2.3.0` - Discord API wrapper
- `python-dotenv>=1.0.0` - Environment variable management
- `aiohttp>=3.8.0` - Async HTTP client (discord.py dependency)
- `fastapi>=0.104.0` - REST API framework
- `uvicorn>=0.24.0` - ASGI server for FastAPI

## Security

Sensitive information (Discord token, API keys, guild IDs) is managed through environment variables in a `.env` file. This file should **never** be committed to version control.

## Future Enhancements

This bot is designed to be extended with additional features such as:
- API authentication/authorization for endpoints
- Webhook integration for role updates
- Database persistence of role information

## Support

For issues and questions, please open an issue on the GitHub repository.
