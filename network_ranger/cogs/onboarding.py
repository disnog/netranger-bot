"""Member onboarding - welcome messages, accept command, member tracking."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from ..bot import NetworkRanger

logger = logging.getLogger(__name__)


class OnboardingCog(commands.Cog, name="Onboarding"):
    """Handles member onboarding flow."""
    
    def __init__(self, bot: "NetworkRanger"):
        self.bot = bot
        self.prune_task.start()
    
    def cog_unload(self):
        self.prune_task.cancel()
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new member joining the server."""
        if member.bot:
            return
        
        guild = member.guild
        
        # Add to database
        await self.bot.db.users.upsert(
            member.id,
            member.name,
            getattr(member, 'discriminator', None),
            member.nick,
            member.joined_at,
        )
        
        # Check if returning member
        permanent_roles = await self.bot.db.users.get_permanent_roles(member.id)
        
        member_role = self.bot.get_member_role(guild)
        eggs_role = self.bot.get_eggs_role(guild)
        member_channel = self.bot.get_member_channel(guild)
        welcome_channel = self.bot.get_welcome_channel(guild)
        
        if "!eggs" in permanent_roles and eggs_role:
            await member.add_roles(eggs_role, reason="Returning eggs member")
        
        if "Member" in permanent_roles and member_role:
            # Returning member - bypass welcome
            await member.add_roles(member_role, reason="Returning member")
            
            if member_channel:
                member_number = await self.bot.db.users.get_member_number(member.id)
                await member_channel.send(
                    f"{member.mention}, welcome back to {guild.name}! "
                    f"We've held on to your previous member number, #{member_number}."
                )
        else:
            # New member - send to welcome channel
            if welcome_channel:
                await welcome_channel.send(
                    f"Hi {member.mention}, welcome to {guild.name}. "
                    f"Please **complete joining the server by accepting the rules** using `/accept`"
                )
    
    @app_commands.command(name="accept", description="Accept the server rules and become a member")
    @app_commands.describe(answer="The answer to the challenge question (hint: TCP)")
    async def accept(self, interaction: discord.Interaction, answer: str):
        """Accept rules and become a member."""
        guild = interaction.guild
        member = interaction.user
        
        member_role = self.bot.get_member_role(guild)
        eggs_role = self.bot.get_eggs_role(guild)
        member_channel = self.bot.get_member_channel(guild)
        
        if not member_role:
            await interaction.response.send_message(
                "Configuration error: Member role not found.",
                ephemeral=True,
            )
            return
        
        # Check if already a member
        if member_role in member.roles:
            await interaction.response.send_message(
                "You're already a member!",
                ephemeral=True,
            )
            return
        
        # Normalize answer
        answer_clean = re.sub(r'\W', '', answer.lower())
        
        if answer_clean == "tcp":
            # Correct answer - make them a member
            await member.add_roles(member_role, reason=f"Accepted rules; Answer: {answer}")
            await self.bot.db.users.add_permanent_role(member.id, "Member")
            member_number = await self.bot.db.users.assign_member_number(member.id)
            
            await interaction.response.send_message(
                f"Welcome to {guild.name}! You are member #{member_number}.",
                ephemeral=True,
            )
            
            if member_channel:
                await member_channel.send(
                    f"{member.mention}, welcome to {guild.name}! You are member #{member_number}, "
                    f"and we're glad to have you. Feel free to take a moment to introduce yourself!"
                )
        
        elif answer_clean == "eggs":
            # Easter egg!
            if eggs_role:
                await member.add_roles(eggs_role, reason="Eggs enthusiast")
                await self.bot.db.users.add_permanent_role(member.id, "!eggs")
            
            await interaction.response.send_message(
                f"🥚 Congratulations! You've joined {eggs_role.mention if eggs_role else '!eggs'}! "
                f"For more information about eggs, please visit https://lmgtfy.app/?q=eggs",
            )
        
        else:
            await interaction.response.send_message(
                "That is not the correct answer. Please try again.",
                ephemeral=True,
            )
    
    @app_commands.command(name="myinfo", description="Show your member profile")
    async def myinfo(self, interaction: discord.Interaction):
        """Show the user's member info."""
        user = await self.bot.db.users.get(interaction.user.id)
        
        if not user:
            await interaction.response.send_message(
                "You're not in the member database yet.",
                ephemeral=True,
            )
            return
        
        embed = discord.Embed(
            title=interaction.user.display_name,
            description=f"{interaction.user.name}",
            color=discord.Color.blue(),
        )
        
        if user.member_number:
            embed.add_field(name="Member Number", value=f"#{user.member_number}")
        
        if user.first_joined_at:
            embed.add_field(
                name="First Joined",
                value=user.first_joined_at.strftime("%Y-%b-%d %H:%M UTC"),
            )
        
        if user.permanent_roles:
            embed.add_field(
                name="Permanent Roles",
                value="\n".join(user.permanent_roles),
                inline=False,
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @tasks.loop(minutes=1)
    async def prune_task(self):
        """Periodically warn and kick non-members who are idling."""
        await self.bot.wait_until_ready()
        
        guild = self.bot.get_guild(self.bot.config.guild_id)
        if not guild:
            return
        
        welcome_channel = self.bot.get_welcome_channel(guild)
        member_role = self.bot.get_member_role(guild)
        
        if not welcome_channel or not member_role:
            return
        
        warning_threshold = timedelta(hours=48)
        kick_threshold = timedelta(hours=72)
        
        for member in welcome_channel.members:
            if member.bot or member_role in member.roles:
                continue
            
            if not member.joined_at:
                continue
            
            time_on_server = datetime.utcnow() - member.joined_at.replace(tzinfo=None)
            
            # Warn at 48 hours
            if warning_threshold <= time_on_server < warning_threshold + timedelta(minutes=1):
                try:
                    await welcome_channel.send(
                        f"{member.mention}, you've been idling in {welcome_channel.name} for {time_on_server}. "
                        f"If you do not accept the rules using `/accept`, you will be removed."
                    )
                except discord.Forbidden:
                    pass
            
            # Kick at 72 hours
            if time_on_server >= kick_threshold:
                try:
                    await member.send(
                        f"You are being removed from {guild.name} because you have not accepted the rules. "
                        f"We'd still love to have you! Feel free to rejoin using the invite link."
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass
                
                try:
                    await guild.kick(
                        member,
                        reason=f"Did not accept rules in {time_on_server}",
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass


async def setup(bot: "NetworkRanger"):
    await bot.add_cog(OnboardingCog(bot))
