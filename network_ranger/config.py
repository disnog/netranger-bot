# config.py
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

"""Bot configuration from environment variables."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Bot configuration."""
    
    # Discord
    token: str
    guild_id: int
    command_prefix: str = "/"  # Legacy, kept for reference
    
    # Channel names
    welcome_channel: str = "welcome"
    member_channel: str = "general"
    log_channel: str = "cnc"
    mirror_channel: str = "mirror"
    
    # Role names
    member_role: str = "Members"
    eggs_role: str = "!eggs"
    
    # Bot info
    description: str = "Network Ranger"
    
    # Email (optional)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None
    
    # Encryption key for email verification
    secret_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment."""
        token = os.environ.get("TOKEN")
        if not token:
            raise ValueError("TOKEN environment variable is required")
        
        guild_id = os.environ.get("GUILD_ID")
        if not guild_id:
            raise ValueError("GUILD_ID environment variable is required")
        
        return cls(
            token=token,
            guild_id=int(guild_id),
            command_prefix=os.environ.get("COMMAND_PREFIX", "/"),
            welcome_channel=os.environ.get("WELCOMECHANNEL_NAME", "welcome"),
            member_channel=os.environ.get("MEMBERCHANNEL_NAME", "general"),
            log_channel=os.environ.get("LOGCHANNEL_NAME", "cnc"),
            mirror_channel=os.environ.get("MIRRORCHANNEL_NAME", "mirror"),
            member_role=os.environ.get("MEMBERROLE_NAME", "Members"),
            eggs_role=os.environ.get("EGGSROLE_NAME", "!eggs"),
            description=os.environ.get("BOT_DESCRIPTION", "Network Ranger"),
            smtp_server=os.environ.get("SMTP_SERVER"),
            smtp_port=int(os.environ.get("SMTP_PORT", "587")),
            smtp_username=os.environ.get("SMTP_USERNAME"),
            smtp_password=os.environ.get("SMTP_PASSWORD"),
            smtp_from=os.environ.get("SMTP_FROMEMAIL"),
            secret_key=os.environ.get("SECRETKEY"),
        )
    
    @property
    def email_configured(self) -> bool:
        """Check if email is configured."""
        return all([
            self.smtp_server,
            self.smtp_username,
            self.smtp_password,
            self.smtp_from,
            self.secret_key,
        ])
