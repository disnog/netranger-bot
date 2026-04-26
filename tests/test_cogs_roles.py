# tests/test_cogs_roles.py
# Unit tests for network_ranger/cogs/roles.py membership gating.

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from network_ranger.cogs.roles import RolesCog


@pytest.fixture
def roles_cog(mock_bot):
    return RolesCog(mock_bot)


@pytest.mark.asyncio
@pytest.mark.parametrize("permanent_role", ["Member", "periphery", "recruiter"])
async def test_require_accepted_member_allows_joined_roles(
    roles_cog,
    mock_bot,
    mock_interaction,
    permanent_role,
):
    mock_bot.db.users.get = AsyncMock(
        return_value=SimpleNamespace(permanent_roles=[permanent_role])
    )

    allowed = await roles_cog._require_accepted_member(mock_interaction)

    assert allowed is True
    mock_interaction.response.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_require_accepted_member_denies_unaccepted_user(
    roles_cog,
    mock_bot,
    mock_interaction,
):
    mock_bot.db.users.get = AsyncMock(
        return_value=SimpleNamespace(permanent_roles=[])
    )

    allowed = await roles_cog._require_accepted_member(mock_interaction)

    assert allowed is False
    mock_interaction.response.send_message.assert_awaited_once()
    args, kwargs = mock_interaction.response.send_message.await_args
    assert "disnog.org/join" in args[0]
    assert kwargs["ephemeral"] is True


@pytest.mark.asyncio
async def test_sendkey_denied_before_email_validation(
    roles_cog,
    mock_bot,
    mock_interaction,
):
    mock_bot.db.users.get = AsyncMock(
        return_value=SimpleNamespace(permanent_roles=[])
    )

    with patch("network_ranger.cogs.roles.validate_email") as mock_validate:
        await roles_cog.sendkey.callback(roles_cog, mock_interaction, "user@example.com")

    mock_validate.assert_not_called()
    mock_interaction.response.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_orgset_denied_before_key_processing(
    roles_cog,
    mock_bot,
    mock_interaction,
):
    mock_bot.db.users.get = AsyncMock(
        return_value=SimpleNamespace(permanent_roles=[])
    )

    with patch.object(roles_cog, "_get_fernet") as mock_get_fernet:
        await roles_cog.orgset.callback(roles_cog, mock_interaction, "opaque-key")

    mock_get_fernet.assert_not_called()
    mock_interaction.response.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_orgclear_denied_before_role_mutation(
    roles_cog,
    mock_bot,
    mock_interaction,
):
    mock_bot.db.users.get = AsyncMock(
        return_value=SimpleNamespace(permanent_roles=[])
    )

    await roles_cog.orgclear.callback(roles_cog, mock_interaction)

    mock_interaction.user.remove_roles.assert_not_awaited()
    mock_interaction.response.send_message.assert_awaited_once()
