"""
Configuration module for Discord Role Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration settings"""
    
    # Bot credentials
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Server IDs
    DEV_GUILD_ID = int(os.getenv('DEV_GUILD_ID', 0)) if os.getenv('DEV_GUILD_ID') else None
    PROD_GUILD_ID = int(os.getenv('PROD_GUILD_ID', 0)) if os.getenv('PROD_GUILD_ID') else None
    
    # Bot settings
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Naja Admin integration
    NAJA_ADMIN_URL = os.getenv('NAJA_ADMIN_URL')
    BOT_API_KEY = os.getenv('BOT_API_KEY')

    # API server
    API_HOST = os.getenv('API_HOST')
    API_PORT = int(os.getenv('API_PORT'))
    
    @property
    def guild_id(self):
        """Get the appropriate guild ID based on environment"""
        if self.ENVIRONMENT == 'production':
            return self.PROD_GUILD_ID
        return self.DEV_GUILD_ID
    
    @property
    def is_development(self):
        """Check if running in development mode"""
        return self.ENVIRONMENT == 'development'
    
    def validate(self):
        """Validate required configuration"""
        if not self.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required")
        
        if not self.guild_id:
            env_var = 'DEV_GUILD_ID' if self.is_development else 'PROD_GUILD_ID'
            raise ValueError(f"{env_var} is required for {self.ENVIRONMENT} environment")

        if not self.BOT_API_KEY:
            raise ValueError("BOT_API_KEY is required")

        if not self.NAJA_ADMIN_URL:
            raise ValueError("NAJA_ADMIN_URL is required")

        if not self.is_development and not self.NAJA_ADMIN_URL.startswith("https://"):
            raise ValueError("NAJA_ADMIN_URL must use HTTPS in production")

        if not self.is_development and self.API_HOST == "0.0.0.0":
            raise ValueError("API_HOST must not be 0.0.0.0 in production")

# Global config instance
config = Config()
