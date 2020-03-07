#!/usr/bin/env python3

#  network-ranger - __main__.py
#  Copyright (C) 2019  Jason R. Rokeach
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
Connect as a Discord bot to maintain the Networking Discord Server.
"""

import discord
import argparse
import os
from discord.ext import commands

token = None
welcome = "welcome"
command_prefix = "$"

# Separate these
try:
    token = os.environ["TOKEN"]
    welcome = os.environ["WELCOME_CHANNEL"]
    bot_description = os.environ["BOT_DESCRIPTION"]
    command_prefix = os.environ["COMMAND_PREFIX"]
except KeyError as e:
    print("Warning: Environmental variable(s) not defined")

parser = argparse.ArgumentParser(
    fromfile_prefix_chars="@", formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("-t", "--token", help="Discord API Token", required=token == "")
parser.add_argument("--welcome", help="Welcome Channel", default=welcome)
parser.add_argument("--command-prefix", help="Command Prefix", default=command_prefix)
parser.add_argument(
    "--bot-description",
    help="Bot Description",
    default="The in-development bot which will maintain the Networking Discord server",
)
args = vars(parser.parse_args())
if "welcome" in args and args["welcome"] is not None:
    welcome = args["welcome"]

if "command_prefix" in args and args["command_prefix"] is not None:
    command_prefix = args["command_prefix"]

if "bot_description" in args and args["bot_description"] is not None:
    bot_description = args["bot_description"]

if "token" in args and args["token"] is not None:
    token = args["token"]

if token is None:
    raise Exception("Cannot start without a token.")

bot = commands.Bot(command_prefix=command_prefix, description=bot_description)


@bot.event
async def on_ready():
    print(
        'Logged in as "{username}" (ID: {userid})'.format(
            username=bot.user.name, userid=bot.user.id
        )
    )
    # TODO: De-hardcode
    global welcomechannel
    welcomechannel = discord.utils.get(
        bot.get_all_channels(), guild__name="Networking", name=welcome
    )
    print(
        "Welcome Channel: {welcomechannel_name} (ID: {welcomechannel_id})".format(
            welcomechannel_name=welcomechannel.name, welcomechannel_id=welcomechannel.id
        )
    )


@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Network Ranger", description=bot_description)
    embed.add_field(name="Author", value="Jason")
    await ctx.send(embed=embed)


@bot.event
async def on_member_join(member):
    """
    Handle users joining the server.
    :param message:
    :return:
    """
    await welcomechannel.send(
        "Welcome to {guild} {mention}".format(
            guild=member.guild.name, mention=member.mention
        )
    )
    print("Welcome", member.mention)


@bot.event
async def on_message(message):
    """
    Handle incoming messages.
    :param message:
    :return:
    """
    if message.author == bot.user:
        return

    if message.content.startswith(command_prefix):
        await process_command(message)


async def process_command(message):
    """
    Process commands prefixed with command_prefix.
    :param message:
    :return:
    """
    command = message.content.lstrip(command_prefix).split()
    await message.channel.send("You said: {}".format(" ".join(command)))


bot.run(token)
