"""Moderation and admin commands."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import NetworkRanger

logger = logging.getLogger(__name__)


class ModerationCog(commands.Cog, name="Moderation"):
    """Admin and moderation commands."""
    
    def __init__(self, bot: "NetworkRanger"):
        self.bot = bot
    
    @app_commands.command(name="botinfo", description="Show bot information")
    @app_commands.default_permissions(ban_members=True)
    async def botinfo(self, interaction: discord.Interaction):
        """Show bot information (mod only)."""
        embed = discord.Embed(
            title="Network Ranger",
            description=self.bot.config.description,
            color=discord.Color.blue(),
        )
        embed.add_field(name="Host", value=os.uname().nodename)
        embed.add_field(name="Guild", value=interaction.guild.name)
        embed.add_field(
            name="GitHub",
            value="https://github.com/disnog/netranger-bot",
            inline=False,
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="syncdb", description="Sync all members to the database")
    @app_commands.default_permissions(administrator=True)
    async def syncdb(self, interaction: discord.Interaction):
        """Force sync all members to database (admin only)."""
        await interaction.response.defer(ephemeral=True)
        
        await self.bot.sync_members(interaction.guild)
        
        await interaction.followup.send(
            "Database sync complete.",
            ephemeral=True,
        )
    
    @app_commands.command(name="lookup", description="Look up a member's database info")
    @app_commands.describe(member="The member to look up")
    @app_commands.default_permissions(ban_members=True)
    async def lookup(self, interaction: discord.Interaction, member: discord.Member):
        """Look up member info (mod only)."""
        user = await self.bot.db.users.get(member.id)
        
        if not user:
            await interaction.response.send_message(
                f"{member.mention} is not in the database.",
                ephemeral=True,
            )
            return
        
        embed = discord.Embed(
            title=f"Member Lookup: {member.display_name}",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Discord ID", value=str(user.id))
        embed.add_field(name="Username", value=user.name)
        embed.add_field(name="Member Number", value=user.member_number or "N/A")
        embed.add_field(
            name="First Joined",
            value=user.first_joined_at.strftime("%Y-%m-%d %H:%M UTC") if user.first_joined_at else "Unknown",
        )
        embed.add_field(
            name="Permanent Roles",
            value=", ".join(user.permanent_roles) or "None",
            inline=False,
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle messages - mirror welcome channel messages."""
        if message.author.bot:
            return
        
        guild = message.guild
        if not guild:
            return
        
        welcome_channel = self.bot.get_welcome_channel(guild)
        if message.channel != welcome_channel:
            return
        
        # Mirror to log channel
        mirror_channel = discord.utils.get(
            guild.text_channels,
            name=self.bot.config.mirror_channel,
        )
        
        if mirror_channel:
            embed = discord.Embed()
            embed.add_field(name="User", value=message.author.name)
            embed.add_field(name="Message", value=message.clean_content[:1000])
            await mirror_channel.send(embed=embed)
        
        # Delete non-admin messages in welcome channel
        try:
            if not message.author.guild_permissions.administrator:
                await message.delete()
        except discord.Forbidden:
            pass


async def setup(bot: "NetworkRanger"):
    await bot.add_cog(ModerationCog(bot))
