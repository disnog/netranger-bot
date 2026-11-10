# tests/test_bot.py
# Unit tests for NetworkRanger behavior that does not require Discord I/O.

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from network_ranger.bot import NetworkRanger


@pytest.mark.asyncio
async def test_sync_members_replaces_permanent_roles_from_current_discord_roles():
    role = SimpleNamespace(id=555666777888999000)
    member = SimpleNamespace(
        id=111222333,
        bot=False,
        roles=[role],
        name="alice",
        discriminator="0",
        nick=None,
        joined_at=None,
    )
    guild = SimpleNamespace(id=123456789, members=[member])
    db = MagicMock()
    db.guilds.get = AsyncMock(
        return_value=SimpleNamespace(
            known_roles=[
                SimpleNamespace(
                    role_id="555666777888999000",
                    significances=["Member"],
                )
            ]
        )
    )
    db.users.upsert = AsyncMock()
    db.users.set_permanent_roles = AsyncMock()
    db.users.assign_missing_member_numbers = AsyncMock(return_value=[])
    bot = SimpleNamespace(db=db)

    await NetworkRanger.sync_members(bot, guild)

    db.users.upsert.assert_awaited_once_with(
        member.id,
        member.name,
        member.discriminator,
        member.nick,
        member.joined_at,
    )
    db.users.set_permanent_roles.assert_awaited_once_with(member.id, ["Member"])


@pytest.mark.asyncio
async def test_sync_members_numbers_members_without_a_number():
    guild = SimpleNamespace(id=123456789, members=[])
    db = MagicMock()
    db.guilds.get = AsyncMock(return_value=SimpleNamespace(known_roles=[]))
    db.users.assign_missing_member_numbers = AsyncMock(return_value=[(1, 41), (2, 42)])
    bot = SimpleNamespace(db=db)

    await NetworkRanger.sync_members(bot, guild)

    db.users.assign_missing_member_numbers.assert_awaited_once_with(with_role="Member")


def _bot_for_on_ready(sync_side_effect=None):
    guild = SimpleNamespace(id=123456789, name="DisNOG")
    bot = MagicMock()
    bot.user = SimpleNamespace(id=1)
    bot._initial_sync_done = False
    bot.get_guild.return_value = guild
    bot.sync_members = AsyncMock(side_effect=sync_side_effect)
    return bot, guild


@pytest.mark.asyncio
async def test_on_ready_syncs_members_once_per_process():
    bot, guild = _bot_for_on_ready()

    await NetworkRanger.on_ready(bot)
    await NetworkRanger.on_ready(bot)  # gateway reconnect with a new session

    bot.sync_members.assert_awaited_once_with(guild)


@pytest.mark.asyncio
async def test_on_ready_retries_sync_after_failure():
    bot, guild = _bot_for_on_ready(sync_side_effect=[RuntimeError("db down"), None])

    await NetworkRanger.on_ready(bot)
    await NetworkRanger.on_ready(bot)
    await NetworkRanger.on_ready(bot)

    assert bot.sync_members.await_count == 2
    assert bot._initial_sync_done is True
