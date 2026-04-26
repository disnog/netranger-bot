# tests/conftest.py
# Shared fixtures for netranger-bot tests.

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

# Provide a minimal valid environment so Config.from_env() works in tests
os.environ.setdefault("TOKEN", "test-bot-token")
os.environ.setdefault("GUILD_ID", "123456789")


@pytest.fixture
def minimal_env(monkeypatch):
    """Set only the required env vars."""
    monkeypatch.setenv("TOKEN", "test-token-abc")
    monkeypatch.setenv("GUILD_ID", "987654321")
    return {"TOKEN": "test-token-abc", "GUILD_ID": "987654321"}


@pytest.fixture
def full_env(monkeypatch):
    """Set all possible env vars."""
    monkeypatch.setenv("TOKEN", "test-token-abc")
    monkeypatch.setenv("GUILD_ID", "987654321")
    monkeypatch.setenv("WELCOMECHANNEL_NAME", "arrivals")
    monkeypatch.setenv("MEMBERCHANNEL_NAME", "lounge")
    monkeypatch.setenv("LOGCHANNEL_NAME", "audit-log")
    monkeypatch.setenv("MIRRORCHANNEL_NAME", "mirror-log")
    monkeypatch.setenv("MEMBERROLE_NAME", "Network Rangers")
    monkeypatch.setenv("BOT_DESCRIPTION", "Test Ranger")
    monkeypatch.setenv("SMTP_SERVER", "mail.example.com")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_USERNAME", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "s3cr3t")
    monkeypatch.setenv("SMTP_FROMEMAIL", "noreply@example.com")
    monkeypatch.setenv("SECRETKEY", "Fernet-compatible-key-32-bytes!!")


@pytest.fixture
def mock_bot():
    """Minimal mock NetworkRanger bot."""
    bot = MagicMock()
    bot.db = MagicMock()
    bot.db.users = MagicMock()
    bot.db.guilds = MagicMock()
    bot.config = MagicMock()
    return bot


@pytest.fixture
def mock_interaction():
    """Mock discord.Interaction for slash command tests."""
    interaction = AsyncMock()
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.guild = MagicMock()
    interaction.guild.id = 123456789
    interaction.user = MagicMock()
    interaction.user.id = 111222333
    interaction.user.roles = []
    interaction.user.add_roles = AsyncMock()
    interaction.user.remove_roles = AsyncMock()
    return interaction
