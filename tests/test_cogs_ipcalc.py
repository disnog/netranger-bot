# tests/test_cogs_ipcalc.py
# Unit tests for network_ranger/cogs/ipcalc.py.

from __future__ import annotations

import ipaddress
from unittest.mock import AsyncMock, MagicMock

import pytest

from network_ranger.cogs.ipcalc import IPCalcCog


@pytest.fixture
def cog(mock_bot):
    return IPCalcCog(mock_bot)


# ---------------------------------------------------------------------------
# _ipv4_info() helper
# ---------------------------------------------------------------------------

def test_ipv4_info_returns_broadcast_and_wildcard(cog):
    net = ipaddress.ip_network("192.168.1.0/24")
    info = cog._ipv4_info(net)

    assert info["broadcast"] == "192.168.1.255"
    assert info["wildcard"] == "0.0.0.255"


def test_ipv4_info_slash30(cog):
    net = ipaddress.ip_network("10.0.0.0/30")
    info = cog._ipv4_info(net)

    assert info["broadcast"] == "10.0.0.3"
    assert info["wildcard"] == "0.0.0.3"


def test_ipv4_info_slash32(cog):
    net = ipaddress.ip_network("192.168.1.1/32")
    info = cog._ipv4_info(net)

    assert info["broadcast"] == "192.168.1.1"
    assert info["wildcard"] == "0.0.0.0"


def test_ipv6_info_returns_empty(cog):
    net = ipaddress.ip_network("2001:db8::/32")
    info = cog._ipv6_info(net)
    assert info == {}


# ---------------------------------------------------------------------------
# ipcalc command — valid input
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ipcalc_valid_ipv4(cog, mock_interaction):
    await cog.ipcalc(mock_interaction, "192.168.1.0/24")

    mock_interaction.response.send_message.assert_called_once()
    kwargs = mock_interaction.response.send_message.call_args[1]
    embed = kwargs["embed"]
    # Verify key embed fields
    field_names = [f.name for f in embed.fields]
    assert "Network" in field_names
    assert "Netmask" in field_names
    assert "CIDR" in field_names
    assert "Broadcast" in field_names


@pytest.mark.asyncio
async def test_ipcalc_valid_ipv6(cog, mock_interaction):
    await cog.ipcalc(mock_interaction, "2001:db8::/32")

    mock_interaction.response.send_message.assert_called_once()
    kwargs = mock_interaction.response.send_message.call_args[1]
    embed = kwargs["embed"]
    field_names = [f.name for f in embed.fields]
    assert "IP Version" in field_names
    # No broadcast field for IPv6
    assert "Broadcast" not in field_names


@pytest.mark.asyncio
async def test_ipcalc_with_host_bits(cog, mock_interaction):
    """strict=False allows host bits to be set."""
    await cog.ipcalc(mock_interaction, "192.168.1.1/24")

    mock_interaction.response.send_message.assert_called_once()
    kwargs = mock_interaction.response.send_message.call_args[1]
    assert "embed" in kwargs


@pytest.mark.asyncio
async def test_ipcalc_private_network(cog, mock_interaction):
    await cog.ipcalc(mock_interaction, "10.0.0.0/8")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    private_field = next(f for f in embed.fields if f.name == "Private")
    assert private_field.value == "Yes"


@pytest.mark.asyncio
async def test_ipcalc_public_network(cog, mock_interaction):
    await cog.ipcalc(mock_interaction, "8.8.8.0/24")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    private_field = next(f for f in embed.fields if f.name == "Private")
    assert private_field.value == "No"


@pytest.mark.asyncio
async def test_ipcalc_slash31_usable_hosts(cog, mock_interaction):
    """A /31 has 2 addresses, 0 usable hosts for IPv4."""
    await cog.ipcalc(mock_interaction, "192.168.1.0/31")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    total_field = next(f for f in embed.fields if f.name == "Total Hosts")
    assert total_field.value == "2"


@pytest.mark.asyncio
async def test_ipcalc_large_network_no_host_list(cog, mock_interaction):
    """Networks > /24 should not list individual hosts."""
    await cog.ipcalc(mock_interaction, "10.0.0.0/8")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    field_names = [f.name for f in embed.fields]
    assert "First Usable" not in field_names


# ---------------------------------------------------------------------------
# ipcalc command — invalid input
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ipcalc_invalid_subnet_sends_error(cog, mock_interaction):
    await cog.ipcalc(mock_interaction, "not-an-ip")

    mock_interaction.response.send_message.assert_called_once()
    args = mock_interaction.response.send_message.call_args
    assert args[1].get("ephemeral") is True
    assert "Invalid" in args[0][0]


@pytest.mark.asyncio
async def test_ipcalc_invalid_cidr_sends_error(cog, mock_interaction):
    await cog.ipcalc(mock_interaction, "192.168.1.0/99")

    args = mock_interaction.response.send_message.call_args
    assert args[1].get("ephemeral") is True


# ---------------------------------------------------------------------------
# ipoverlap command — overlapping subnets
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ipoverlap_detects_overlap(cog, mock_interaction):
    await cog.ipoverlap(mock_interaction, "192.168.1.0/24", "192.168.1.128/25")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    result_field = next(f for f in embed.fields if f.name == "Result")
    assert "OVERLAP" in result_field.value


@pytest.mark.asyncio
async def test_ipoverlap_subnet_contained_within(cog, mock_interaction):
    """192.168.1.128/25 is a subnet of 192.168.1.0/24."""
    await cog.ipoverlap(mock_interaction, "192.168.1.0/24", "192.168.1.128/25")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    detail_field = next((f for f in embed.fields if f.name == "Detail"), None)
    assert detail_field is not None
    assert "contained within" in detail_field.value


@pytest.mark.asyncio
async def test_ipoverlap_no_overlap(cog, mock_interaction):
    await cog.ipoverlap(mock_interaction, "10.0.0.0/24", "10.0.1.0/24")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    result_field = next(f for f in embed.fields if f.name == "Result")
    assert "No overlap" in result_field.value


@pytest.mark.asyncio
async def test_ipoverlap_identical_subnets(cog, mock_interaction):
    await cog.ipoverlap(mock_interaction, "10.0.0.0/24", "10.0.0.0/24")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    result_field = next(f for f in embed.fields if f.name == "Result")
    assert "OVERLAP" in result_field.value


@pytest.mark.asyncio
async def test_ipoverlap_partial_overlap(cog, mock_interaction):
    """10.0.0.128/25 and 10.0.0.192/26 partially overlap."""
    await cog.ipoverlap(mock_interaction, "10.0.0.128/25", "10.0.0.192/26")

    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    result_field = next(f for f in embed.fields if f.name == "Result")
    assert "OVERLAP" in result_field.value


# ---------------------------------------------------------------------------
# ipoverlap command — invalid input
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ipoverlap_invalid_first_subnet(cog, mock_interaction):
    await cog.ipoverlap(mock_interaction, "bad-input", "10.0.0.0/24")

    args = mock_interaction.response.send_message.call_args
    assert args[1].get("ephemeral") is True


@pytest.mark.asyncio
async def test_ipoverlap_invalid_second_subnet(cog, mock_interaction):
    await cog.ipoverlap(mock_interaction, "10.0.0.0/24", "also-bad")

    args = mock_interaction.response.send_message.call_args
    assert args[1].get("ephemeral") is True


# ---------------------------------------------------------------------------
# Network calculations (pure Python, no Discord)
# ---------------------------------------------------------------------------

def test_ipv4_network_num_addresses():
    net = ipaddress.ip_network("10.0.0.0/24")
    assert net.num_addresses == 256


def test_ipv4_network_usable_hosts():
    net = ipaddress.ip_network("10.0.0.0/24")
    hosts = list(net.hosts())
    assert len(hosts) == 254
    assert str(hosts[0]) == "10.0.0.1"
    assert str(hosts[-1]) == "10.0.0.254"


def test_ipv6_network_properties():
    net = ipaddress.ip_network("2001:db8::/48")
    assert net.version == 6
    assert net.prefixlen == 48


def test_overlaps_detection():
    net1 = ipaddress.ip_network("192.168.0.0/23")
    net2 = ipaddress.ip_network("192.168.1.0/24")
    assert net1.overlaps(net2) is True


def test_no_overlap_detection():
    net1 = ipaddress.ip_network("192.168.0.0/24")
    net2 = ipaddress.ip_network("192.168.1.0/24")
    assert net1.overlaps(net2) is False
