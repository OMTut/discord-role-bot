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

# Global config instance
config = Config()
