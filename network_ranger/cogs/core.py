#!/usr/bin/config python3

#  network_ranger - cogs/core.py
#  Copyright (C) 2020  Jason R. Rokeach
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Core cog
"""

from discord.ext import tasks, commands
import discord
from classes import Config
from network_ranger.cogs.background_timer import BackgroundTimer

conf = Config()


async def is_guild_admin(ctx):
    return ctx.author.guild_permissions.administrator


class Core(commands.Cog):
    loadable_cogs = {"BackgroundTimer": {}}

    def __init__(self, bot):
        self.bot = bot

    @commands.group(help="Bot cog operations")
    @commands.check(is_guild_admin)
    async def cogs(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "{mention}: Invalid subcommand.".format(mention=ctx.author.mention)
            )

    @cogs.group(help="List cogs")
    async def list(self, ctx):
        # Delete the message if it hasn't already been deleted.
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass
        embed = discord.Embed(title="Cogs")
        cogs = list(self.bot.cogs.keys())
        permanent_cogs = cogs.copy()
        unloaded_cogs = list(self.loadable_cogs.keys())
        loaded_cogs = list()
        for cog in cogs:
            if cog in unloaded_cogs:
                loaded_cogs.append(cog)
                unloaded_cogs.remove(cog)
                permanent_cogs.remove(cog)
        if not len(loaded_cogs):
            loaded_cogs.append("*(None)*")
        if not len(unloaded_cogs):
            unloaded_cogs.append("*(None)*")
        if not len(permanent_cogs):
            permanent_cogs.append("*(None)*")
        embed.add_field(name="Permanent Cogs", value="\r\n".join(permanent_cogs))
        embed.add_field(name="Loaded Cogs", value="\r\n".join(loaded_cogs))
        embed.add_field(name="Unloaded Cogs", value="\r\n".join(unloaded_cogs))
        await ctx.send(embed=embed)