# bot.py
# Copyright (C) 2020-2026 DisNOG.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Main bot class with discord.py 2.x."""

from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands

from netranger_db import Database

from .config import Config

logger = logging.getLogger(__name__)


class NetworkRanger(commands.Bot):
    """The Network Ranger Discord bot."""
    
    def __init__(self, config: Config):
        self.config = config
        self._db: Optional[Database] = None
        
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(
            command_prefix=commands.when_mentioned,  # Only respond to mentions for legacy commands
            intents=intents,
            description=config.description,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the network",
            ),
        )
    
    @property
    def db(self) -> Database:
        """Get database connection."""
        if self._db is None:
            raise RuntimeError("Database not connected")
        return self._db
    
    async def setup_hook(self) -> None:
        """Called when the bot is starting up."""
        # Connect to database
        self._db = Database.from_env()
        await self._db.connect()
        logger.info("Database connected")
        
        # Load cogs
        await self.load_extension("network_ranger.cogs.onboarding")
        await self.load_extension("network_ranger.cogs.ipcalc")
        await self.load_extension("network_ranger.cogs.roles")
        await self.load_extension("network_ranger.cogs.moderation")
        logger.info("Cogs loaded")
        
        # Sync slash commands to the guild
        guild = discord.Object(id=self.config.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info(f"Commands synced to guild {self.config.guild_id}")
    
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        
        # Get references to important channels/roles
        guild = self.get_guild(self.config.guild_id)
        if guild:
            logger.info(f"Connected to guild: {guild.name}")
            
            # Sync existing members to database
            await self.sync_members(guild)
    
    async def sync_members(self, guild: discord.Guild) -> None:
        """Sync all guild members to the database."""
        # Get known roles from database
        db_guild = await self.db.guilds.get(str(guild.id))
        if not db_guild:
            return
        
        known_role_map = {}
        for role in db_guild.known_roles:
            known_role_map[role.role_id] = role.significances
        
        count = 0
        for member in guild.members:
            if member.bot:
                continue
            
            # Determine permanent roles from current Discord roles
            permanent_roles = []
            for role in member.roles:
                if str(role.id) in known_role_map:
                    permanent_roles.extend(known_role_map[str(role.id)])
            
            # Upsert user
            await self.db.users.upsert(
                member.id,
                member.name,
                member.discriminator if hasattr(member, 'discriminator') else None,
                member.nick,
                member.joined_at,
            )
            
            # Add permanent roles
            for role_sig in permanent_roles:
                await self.db.users.add_permanent_role(member.id, role_sig)
            
            count += 1
        
        logger.info(f"Synced {count} members to database")
    
    async def close(self) -> None:
        """Clean up when bot is shutting down."""
        if self._db:
            await self._db.close()
        await super().close()
    
    def get_welcome_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the welcome channel for a guild."""
        return discord.utils.get(guild.text_channels, name=self.config.welcome_channel)
    
    def get_member_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the member channel for a guild."""
        return discord.utils.get(guild.text_channels, name=self.config.member_channel)
    
    def get_log_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the log channel for a guild."""
        return discord.utils.get(guild.text_channels, name=self.config.log_channel)
    
    def get_member_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Get the member role for a guild."""
        return discord.utils.get(guild.roles, name=self.config.member_role)
    
    def get_eggs_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Get the eggs role for a guild."""
        return discord.utils.get(guild.roles, name=self.config.eggs_role)
