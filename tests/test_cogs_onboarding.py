# tests/test_cogs_onboarding.py
# Unit tests for onboarding member-join behavior.

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from network_ranger.cogs.onboarding import OnboardingCog


@pytest.fixture
def onboarding_cog(mock_bot):
    return OnboardingCog(mock_bot)


def _build_member(*, guild_name: str = "DisNOG"):
    guild = MagicMock()
    guild.id = 123456789
    guild.name = guild_name
    guild.get_role = MagicMock(return_value=None)

    member = MagicMock()
    member.id = 111222333
    member.bot = False
    member.guild = guild
    member.name = "alice"
    member.nick = None
    member.discriminator = "0"
    member.joined_at = None
    member.mention = "<@111222333>"
    member.roles = []
    member.add_roles = AsyncMock()
    return member


@pytest.mark.asyncio
async def test_new_member_without_permanent_roles_gets_join_prompt(onboarding_cog, mock_bot):
    member = _build_member()
    welcome_channel = MagicMock()
    welcome_channel.send = AsyncMock()

    mock_bot.db.users.upsert = AsyncMock()
    mock_bot.db.users.get_permanent_roles = AsyncMock(return_value=[])
    mock_bot.db.users.get_member_number = AsyncMock()
    mock_bot.db.users.assign_member_number = AsyncMock()
    mock_bot.db.guilds.get = AsyncMock(return_value=None)
    mock_bot.get_member_role.return_value = MagicMock()
    mock_bot.get_member_channel.return_value = MagicMock()
    mock_bot.get_welcome_channel.return_value = welcome_channel

    await onboarding_cog.on_member_join(member)

    member.add_roles.assert_not_awaited()
    mock_bot.db.users.assign_member_number.assert_not_awaited()
    mock_bot.db.users.add_permanent_role.assert_not_called()
    welcome_channel.send.assert_awaited_once()
    assert "disnog.org/join" in welcome_channel.send.await_args.args[0]


@pytest.mark.asyncio
async def test_returning_member_restores_role_and_welcomes_back(onboarding_cog, mock_bot):
    member = _build_member()
    member_role = MagicMock()
    member_channel = MagicMock()
    member_channel.send = AsyncMock()

    mock_bot.db.users.upsert = AsyncMock()
    mock_bot.db.users.get_permanent_roles = AsyncMock(return_value=["Member"])
    mock_bot.db.users.get_member_number = AsyncMock(return_value=42)
    mock_bot.db.users.assign_member_number = AsyncMock()
    mock_bot.db.guilds.get = AsyncMock(
        return_value=SimpleNamespace(
            known_roles=[
                SimpleNamespace(role_id="555666777888999000", significances=["Member"])
            ]
        )
    )
    member.guild.get_role.return_value = member_role
    mock_bot.get_member_role.return_value = member_role
    mock_bot.get_member_channel.return_value = member_channel
    mock_bot.get_welcome_channel.return_value = MagicMock()

    await onboarding_cog.on_member_join(member)

    member.add_roles.assert_awaited_once_with(member_role, reason="Restoring permanent roles")
    mock_bot.db.users.assign_member_number.assert_not_awaited()
    member_channel.send.assert_awaited_once()
    sent = member_channel.send.await_args.args[0]
    assert "welcome back" in sent.lower()
    assert "#42" in sent


@pytest.mark.asyncio
async def test_member_without_number_gets_assigned_number(onboarding_cog, mock_bot):
    member = _build_member()
    member_role = MagicMock()
    member.roles = [member_role]
    member_channel = MagicMock()
    member_channel.send = AsyncMock()

    mock_bot.db.users.upsert = AsyncMock()
    mock_bot.db.users.get_permanent_roles = AsyncMock(return_value=["Member"])
    mock_bot.db.users.get_member_number = AsyncMock(return_value=None)
    mock_bot.db.users.assign_member_number = AsyncMock(return_value=77)
    mock_bot.db.guilds.get = AsyncMock(return_value=None)
    mock_bot.get_member_role.return_value = member_role
    mock_bot.get_member_channel.return_value = member_channel
    mock_bot.get_welcome_channel.return_value = MagicMock()

    await onboarding_cog.on_member_join(member)

    member.add_roles.assert_not_awaited()
    mock_bot.db.users.assign_member_number.assert_awaited_once_with(member.id)
    member_channel.send.assert_awaited_once()
    assert "#77" in member_channel.send.await_args.args[0]
