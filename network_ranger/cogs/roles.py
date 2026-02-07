# roles.py
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

"""Role management commands - org verification via email."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands
from cryptography.fernet import Fernet, InvalidToken
from email_validator import validate_email, EmailNotValidError
import aiosmtplib
from email.message import EmailMessage

if TYPE_CHECKING:
    from ..bot import NetworkRanger

logger = logging.getLogger(__name__)


class RolesCog(commands.Cog, name="Roles"):
    """Role management including org verification."""
    
    def __init__(self, bot: "NetworkRanger"):
        self.bot = bot
    
    def _get_fernet(self) -> Optional[Fernet]:
        """Get Fernet instance for encryption."""
        if not self.bot.config.secret_key:
            return None
        return Fernet(self.bot.config.secret_key.encode())
    
    async def _send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email."""
        if not self.bot.config.email_configured:
            return False
        
        message = EmailMessage()
        message["From"] = self.bot.config.smtp_from
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        
        try:
            await aiosmtplib.send(
                message,
                hostname=self.bot.config.smtp_server,
                port=self.bot.config.smtp_port,
                username=self.bot.config.smtp_username,
                password=self.bot.config.smtp_password,
                start_tls=True,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    @app_commands.command(name="sendkey", description="Send an email verification key for org affiliation")
    @app_commands.describe(email="Your work email address")
    async def sendkey(self, interaction: discord.Interaction, email: str):
        """Send email verification key."""
        # Validate email
        try:
            valid = validate_email(email)
            email = valid.email
            domain = valid.domain
        except EmailNotValidError as e:
            await interaction.response.send_message(
                f"Invalid email: {e}",
                ephemeral=True,
            )
            return
        
        # Check if email is configured
        fernet = self._get_fernet()
        if not fernet or not self.bot.config.email_configured:
            await interaction.response.send_message(
                "Email verification is not configured on this bot.",
                ephemeral=True,
            )
            return
        
        # Create encrypted key
        key_data = json.dumps({"uid": str(interaction.user.id), "email": email})
        key = fernet.encrypt(key_data.encode()).decode()
        
        # Send email
        subject = "Networking Discord Email Validation Key"
        body = f"""Your validation key is:

{key}

To activate an org affiliation role, in the Discord server, use:
/orgset key:{key}

Note: This will remove your current org affiliation role, if any.
"""
        
        await interaction.response.defer(ephemeral=True)
        
        if await self._send_email(email, subject, body):
            await interaction.followup.send(
                f"I've emailed you at {domain} to verify your association. "
                f"Check your email for the validation instructions.",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                "Failed to send verification email. Please try again later.",
                ephemeral=True,
            )
    
    @app_commands.command(name="orgset", description="Set your org affiliation using a verification key")
    @app_commands.describe(key="The verification key from your email")
    async def orgset(self, interaction: discord.Interaction, key: str):
        """Set org affiliation role using email key."""
        fernet = self._get_fernet()
        if not fernet:
            await interaction.response.send_message(
                "Email verification is not configured.",
                ephemeral=True,
            )
            return
        
        try:
            # Decrypt and validate key
            key_data = json.loads(fernet.decrypt(key.encode()).decode())
            
            if key_data.get("uid") != str(interaction.user.id):
                await interaction.response.send_message(
                    "Invalid key - this key was not generated for you.",
                    ephemeral=True,
                )
                return
            
            email = key_data.get("email")
            valid = validate_email(email)
            domain = valid.domain
            
        except (InvalidToken, json.JSONDecodeError, EmailNotValidError):
            await interaction.response.send_message(
                "Invalid or expired key.",
                ephemeral=True,
            )
            return
        
        guild = interaction.guild
        member = interaction.user
        
        # Remove existing org roles
        for role in member.roles:
            if role.name.startswith("org:"):
                await member.remove_roles(role, reason="Changing org affiliation")
                if len(role.members) == 0:
                    await role.delete(reason="Last member removed from org role")
        
        # Find or create org role
        role_name = f"org:{domain}"
        org_role = discord.utils.get(guild.roles, name=role_name)
        
        if not org_role:
            org_role = await guild.create_role(name=role_name)
        
        await member.add_roles(org_role, reason=f"Verified email at {domain}")
        
        await interaction.response.send_message(
            f"Your org affiliation has been set to **{domain}**",
            ephemeral=True,
        )
    
    @app_commands.command(name="orgclear", description="Remove your org affiliation role")
    async def orgclear(self, interaction: discord.Interaction):
        """Clear org affiliation."""
        member = interaction.user
        removed = False
        
        for role in member.roles:
            if role.name.startswith("org:"):
                await member.remove_roles(role, reason="User cleared org affiliation")
                if len(role.members) == 0:
                    await role.delete(reason="Last member removed from org role")
                removed = True
        
        if removed:
            await interaction.response.send_message(
                "Your org affiliation has been cleared.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "You don't have an org affiliation role.",
                ephemeral=True,
            )


async def setup(bot: "NetworkRanger"):
    await bot.add_cog(RolesCog(bot))
