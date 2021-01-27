#!/usr/bin/config python3

#  network_ranger - cogs/background_timer.py
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
Timer cog for background processes
"""

from discord.ext import tasks, commands
import discord
from classes import Config
from datetime import datetime

conf = Config()


class BackgroundTimer(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.minutetimer.start()

    def cog_unload(self):
        self.minutetimer.cancel()

    @tasks.loop(seconds=60.0)
    async def minutetimer(self):
        await self.prune_non_members()

    @minutetimer.before_loop
    async def before_minutetimer(self):
        # Wait until the bot is ready
        await self.bot.wait_until_ready()

    async def prune_non_members(self):
        # Build a list of members to kick if they've been sitting in the welcome channel more than 3 days.
        warning_seconds = 172800
        kick_seconds = 259200
        welcomechannel = discord.utils.get(
            self.bot.guilds[0].channels, name=conf.get("welcomechannel_name")
        )
        memberrole = discord.utils.get(
            self.bot.guilds[0].roles, name=conf.get("memberrole_name")
        )
        for member in welcomechannel.members:
            if memberrole not in member.roles and not member.bot:
                time_on_server = datetime.utcnow() - member.joined_at
                if 0 <= time_on_server.total_seconds() - warning_seconds < 60:
                    # Warn them that they're going to be kicked if they continue to idle.
                    await welcomechannel.send(
                        "{mention}, you've been idling in {welcome_channel} for {time}. If you do not "
                        "`{command_prefix}accept`, you will be removed and will need to rejoin.".format(
                            mention=member.mention,
                            welcome_channel=welcomechannel.name,
                            time=time_on_server,
                            command_prefix=self.bot.command_prefix,
                        )
                    )
                if time_on_server.total_seconds() > kick_seconds:
                    # Kick the user for not accepting.
                    try:
                        await member.send(
                            "You are being removed from {server} because you have not accepted the rules. We'd still love"
                            " to have you if you're interested in network engineering. If you wish to rejoin, please feel"
                            " free to do so using the join link at {url}.".format(
                                server=self.bot.guilds[0].name,
                                url="https://discord.neteng.xyz",
                            )
                        )
                    except discord.errors.Forbidden:
                        pass
                    except discord.errors.HTTPException:
                        pass
                    try:
                        await welcomechannel.guild.kick(
                            member,
                            reason="Did not accept the rules in {time}".format(
                                time=time_on_server
                            ),
                        )
                    except discord.errors.Forbidden:
                        pass
                    except discord.errors.HTTPException:
                        pass
