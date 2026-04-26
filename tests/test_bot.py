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
