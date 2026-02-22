# onboarding.py
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

"""Member onboarding - welcome messages and member tracking."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import NetworkRanger

logger = logging.getLogger(__name__)


class OnboardingCog(commands.Cog, name="Onboarding"):
    """Handles member onboarding flow."""

    def __init__(self, bot: "NetworkRanger"):
        self.bot = bot
    
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
        member_channel = self.bot.get_member_channel(guild)
        welcome_channel = self.bot.get_welcome_channel(guild)

        if "Member" in permanent_roles and member_role:
            # Returning member - restore their roles
            await member.add_roles(member_role, reason="Returning member")

            # Assign member number if they don't have one
            member_number = await self.bot.db.users.get_member_number(member.id)
            if not member_number:
                member_number = await self.bot.db.users.assign_member_number(member.id)

            if member_channel:
                await member_channel.send(
                    f"{member.mention}, welcome back to {guild.name}! "
                    f"We've held on to your previous member number, #{member_number}."
                )
        else:
            # New member - add member role automatically and assign number
            if member_role:
                await member.add_roles(member_role, reason="New member")
                await self.bot.db.users.add_permanent_role(member.id, "Member")
                member_number = await self.bot.db.users.assign_member_number(member.id)

                # Send welcome message
                if welcome_channel:
                    await welcome_channel.send(
                        f"Hi {member.mention}, welcome to {guild.name}! You are member #{member_number}."
                    )

                if member_channel:
                    await member_channel.send(
                        f"{member.mention}, welcome to {guild.name}! You are member #{member_number}, "
                        f"and we're glad to have you. Feel free to take a moment to introduce yourself!"
                    )
            elif welcome_channel:
                # Fallback if member role not configured
                await welcome_channel.send(
                    f"Hi {member.mention}, welcome to {guild.name}!"
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


async def setup(bot: "NetworkRanger"):
    await bot.add_cog(OnboardingCog(bot))
