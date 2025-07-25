"""
Role management utilities for Discord Role Bot
"""
import discord
from typing import List, Dict

###########################################
# Get Guild Roles
# Params: guild (discord.Guild)
# Returns: List of roles excluding managed roles and @everyone
###########################################
def get_guild_roles(guild: discord.Guild) -> List[Dict[str, any]]:
    try:
        roles = []
        for role in guild.roles:
            if not role.managed and role.name != "@everyone":
                roles.append({'name': role.name, 'id': role.id})
        return roles
    except Exception as e:
        print(f"Error fetching roles: {e}")
        return []


