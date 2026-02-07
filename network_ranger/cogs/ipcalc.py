# ipcalc.py
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

"""IP subnet calculator commands."""

from __future__ import annotations

import ipaddress
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import NetworkRanger


class IPCalcCog(commands.Cog, name="IP Calculator"):
    """IP subnet calculation commands."""
    
    def __init__(self, bot: "NetworkRanger"):
        self.bot = bot
    
    @app_commands.command(name="ipcalc", description="Calculate IP subnet information")
    @app_commands.describe(subnet="IP address with CIDR notation (e.g., 192.168.1.0/24)")
    async def ipcalc(self, interaction: discord.Interaction, subnet: str):
        """Display information about an IP subnet."""
        try:
            network = ipaddress.ip_network(subnet, strict=False)
        except ValueError as e:
            await interaction.response.send_message(
                f"Invalid subnet: {e}",
                ephemeral=True,
            )
            return
        
        
        embed = discord.Embed(
            title="IP Subnet Calculator",
            color=discord.Color.green(),
        )
        embed.add_field(name="Input", value=subnet, inline=False)
        embed.add_field(name="Network", value=str(network.network_address), inline=True)
        embed.add_field(name="Netmask", value=str(network.netmask), inline=True)
        embed.add_field(name="CIDR", value=f"/{network.prefixlen}", inline=True)
        
        if network.version == 4:
            embed.add_field(name="Broadcast", value=str(network.broadcast_address), inline=True)
            embed.add_field(name="Wildcard", value=str(network.hostmask), inline=True)
        
        embed.add_field(name="Total Hosts", value=f"{network.num_addresses:,}", inline=True)
        
        if network.num_addresses <= 256:
            usable = max(0, network.num_addresses - 2) if network.version == 4 else network.num_addresses
            embed.add_field(name="Usable Hosts", value=f"{usable:,}", inline=True)
            
            if network.num_addresses > 2:
                hosts = list(network.hosts())
                if hosts:
                    embed.add_field(name="First Usable", value=str(hosts[0]), inline=True)
                    embed.add_field(name="Last Usable", value=str(hosts[-1]), inline=True)
        
        embed.add_field(name="IP Version", value=f"IPv{network.version}", inline=True)
        embed.add_field(name="Private", value="Yes" if network.is_private else "No", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ipoverlap", description="Check if two subnets overlap")
    @app_commands.describe(
        subnet1="First subnet (e.g., 192.168.1.0/24)",
        subnet2="Second subnet (e.g., 192.168.1.128/25)",
    )
    async def ipoverlap(self, interaction: discord.Interaction, subnet1: str, subnet2: str):
        """Check if two IP subnets overlap."""
        try:
            net1 = ipaddress.ip_network(subnet1, strict=False)
            net2 = ipaddress.ip_network(subnet2, strict=False)
        except ValueError as e:
            await interaction.response.send_message(
                f"Invalid subnet: {e}",
                ephemeral=True,
            )
            return
        
        overlaps = net1.overlaps(net2)
        
        embed = discord.Embed(
            title="Subnet Overlap Check",
            color=discord.Color.red() if overlaps else discord.Color.green(),
        )
        embed.add_field(name="Subnet 1", value=str(net1), inline=True)
        embed.add_field(name="Subnet 2", value=str(net2), inline=True)
        embed.add_field(
            name="Result",
            value="⚠️ **OVERLAP DETECTED**" if overlaps else "✅ No overlap",
            inline=False,
        )
        
        if overlaps:
            # Find the overlap
            if net1.subnet_of(net2):
                embed.add_field(name="Detail", value=f"{net1} is contained within {net2}")
            elif net2.subnet_of(net1):
                embed.add_field(name="Detail", value=f"{net2} is contained within {net1}")
            else:
                embed.add_field(name="Detail", value="Subnets partially overlap")
        
        await interaction.response.send_message(embed=embed)
    
    def _ipv4_info(self, network: ipaddress.IPv4Network) -> dict:
        """Get IPv4-specific info."""
        return {
            "broadcast": str(network.broadcast_address),
            "wildcard": str(network.hostmask),
        }
    
    def _ipv6_info(self, network: ipaddress.IPv6Network) -> dict:
        """Get IPv6-specific info."""
        return {}


async def setup(bot: "NetworkRanger"):
    await bot.add_cog(IPCalcCog(bot))
