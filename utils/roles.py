"""
Role management utilities for Discord Role Bot
"""
import discord
import logging
from typing import List, Dict, Set

audit_log = logging.getLogger("gibbs.audit")

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
        audit_log.error(f"Error fetching roles: {e}")
        return []


###########################################
# Set Member Roles
# Params: guild, discord_user_id (str), assigned_role_discord_ids, managed_role_discord_ids
# Only touches roles that ORG Admin manages; leaves all other Discord roles intact.
###########################################
async def get_member_role_ids(guild: discord.Guild, discord_user_id: str) -> List[str] | None:
    """Return the member's current role IDs (excluding @everyone). None if member not found."""
    try:
        member = guild.get_member(int(discord_user_id))
        if not member:
            member = await guild.fetch_member(int(discord_user_id))
        if not member:
            return None
        return [str(role.id) for role in member.roles if role.id != guild.id]
    except Exception:
        return None


async def set_member_roles(
    guild: discord.Guild,
    discord_user_id: str,
    assigned_role_discord_ids: List[str],
    managed_role_discord_ids: List[str],
) -> tuple[List[str], List[str]]:
    """
    Returns (final_managed_role_ids, errors).
    final_managed_role_ids: the managed Discord role IDs now on the member after changes.
    errors: human-readable messages for any roles that could not be changed.
    """
    try:
        member = guild.get_member(int(discord_user_id))
        if not member:
            member = await guild.fetch_member(int(discord_user_id))
        if not member:
            return [], [f"Member {discord_user_id} not found in guild"]

        managed: Set[str] = set(managed_role_discord_ids)
        assigned: Set[str] = set(assigned_role_discord_ids)

        if not assigned.issubset(managed):
            invalid = assigned - managed
            return [], [], [f"Assigned roles not in managed set: {invalid}"]

        guild_roles_by_id = {str(role.id): role for role in guild.roles}
        current_managed = {str(r.id) for r in member.roles if str(r.id) in managed}

        to_remove = current_managed - assigned
        to_add = assigned - current_managed

        successful_removes: Set[str] = set()
        successful_adds: Set[str] = set()
        not_in_discord: Set[str] = set()
        errors = []

        for role_id in to_remove:
            role = guild_roles_by_id.get(role_id)
            if role:
                try:
                    await member.remove_roles(role)
                    successful_removes.add(role_id)
                except Exception as e:
                    errors.append(f"'{role.name}': {e}")

        for role_id in to_add:
            role = guild_roles_by_id.get(role_id)
            if role and not role.managed:
                try:
                    await member.add_roles(role)
                    successful_adds.add(role_id)
                except Exception as e:
                    errors.append(f"'{role.name}': {e}")
            else:
                # Role not found in guild — app-only, ORG Admin should save it directly
                not_in_discord.add(role_id)

        final = (current_managed - successful_removes) | successful_adds

        if successful_adds or successful_removes:
            audit_log.info(
                "Role update: user=%s added=[%s] removed=[%s]",
                discord_user_id,
                ", ".join(successful_adds),
                ", ".join(successful_removes),
            )
        else:
            audit_log.info("Role update: user=%s no_changes", discord_user_id)

        if errors:
            audit_log.warning("Role update errors: user=%s errors=%s", discord_user_id, errors)

        return list(final), list(not_in_discord), errors
    except Exception as e:
        audit_log.error("Role update failed: user=%s error=%s", discord_user_id, str(e))
        return [], [], [str(e)]
