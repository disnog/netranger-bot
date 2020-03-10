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
welcomechannel_name = "welcome"
memberrole_name = "Members"
logchannel_name = "mods-cnc"
command_prefix = "$"
welcome_message = "Hi {mention}, welcome to {server}!"
bot_description = "The Networking Discord Bot"

# TODO: Handle these in a loop
# TODO: Document environment variables
try:
    token = os.environ["TOKEN"]
except KeyError as e:
    print("Warning: Environment variable", e.args[0], "not defined")

try:
    welcomechannel_name = os.environ["WELCOMECHANNEL_NAME"]
except KeyError as e:
    print("Warning: Environment variable", e.args[0], "not defined")

try:
    memberrole_name = os.environ["MEMBERROLE_NAME"]
except KeyError as e:
    print("Warning: Environment variable", e.args[0], "not defined")

try:
    logchannel_name = os.environ["LOGCHANNEL_NAME"]
except KeyError as e:
    print("Warning: Environment variable", e.args[0], "not defined")

try:
    bot_description = os.environ["BOT_DESCRIPTION"]
except KeyError as e:
    print("Warning: Environment variable", e.args[0], "not defined")

try:
    command_prefix = os.environ["COMMAND_PREFIX"]
except KeyError as e:
    print("Warning: Environment variable", e.args[0], "not defined")

try:
    welcome_message = os.environ["WELCOME_MESSAGE"]
except KeyError as e:
    print("Warning: Environment variable", e.args[0], "not defined")

parser = argparse.ArgumentParser(
    fromfile_prefix_chars="@", formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("-t", "--token", help="Discord API Token", required=token == "")
parser.add_argument(
    "--welcome-channel", help="Welcome Channel Name (No #)", default=welcomechannel_name
)
parser.add_argument("--member-role", help="Member Role Name", default=memberrole_name)
parser.add_argument("--log-channel", help="Log Channel", default=logchannel_name)
parser.add_argument(
    "--welcome-message", help="Welcome Message", default=welcome_message
)
parser.add_argument("--command-prefix", help="Command Prefix", default=command_prefix)
parser.add_argument(
    "--bot-description", help="Bot Description", default=bot_description
)
args = vars(parser.parse_args())
if "welcome_channel" in args and args["welcome_channel"] is not None:
    welcomechannel_name = args["welcome_channel"]

if "member_role" in args and args["member_role"] is not None:
    memberrole_name = args["member_role"]

if "log_channel" in args and args["log_channel"] is not None:
    logchannel_name = args["log_channel"]

if "welcome_message" in args and args["welcome_message"] is not None:
    welcome_message = args["welcome_message"]

if "command_prefix" in args and args["command_prefix"] is not None:
    command_prefix = args["command_prefix"]

if "bot_description" in args and args["bot_description"] is not None:
    bot_description = args["bot_description"]

if "token" in args and args["token"] is not None:
    token = args["token"]

if token is None:
    raise Exception("Cannot start without a token.")

bot = commands.Bot(
    command_prefix=command_prefix,
    description=bot_description,
    # TODO: De-hardcode activity
    activity=discord.Activity(
        type=discord.ActivityType.playing,
        name="Network Ranger",
        url="https://github.com/Networking-discord/network-ranger",
    ),
)


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
        bot.get_all_channels(), guild__name="Networking", name=welcomechannel_name
    )
    print(
        "Welcome Channel: {welcomechannel_name} (ID: {welcomechannel_id})".format(
            welcomechannel_name=welcomechannel.name, welcomechannel_id=welcomechannel.id
        )
    )
    global memberrole
    memberrole = discord.utils.get(welcomechannel.guild.roles, name=memberrole_name)
    print(
        "Member Role: {memberrole_name} (ID: {memberrole_id})".format(
            memberrole_name=memberrole.name, memberrole_id=memberrole.id
        )
    )
    global logchannel
    logchannel = discord.utils.get(
        bot.get_all_channels(), guild__name="Networking", name=logchannel_name
    )
    print(
        "Log Channel: {logchannel_name} (ID: {logchannel_id})".format(
            logchannel_name=logchannel.name, logchannel_id=logchannel.id
        )
    )
    await logchannel.send(
        "Bot Online. Command prefix: {command_prefix}".format(
            command_prefix=command_prefix
        )
    )


@bot.command(help="Shows bot information")
async def info(ctx):
    embed = discord.Embed(title="Network Ranger", description=bot_description)
    embed.add_field(name="Command Prefix", value=command_prefix)
    embed.add_field(
        name="Github", value="https://github.com/networking-discord/network-ranger"
    )
    await ctx.send(embed=embed)


@bot.command(help="Answer the challenge question in #{}".format(welcomechannel_name))
async def accept(ctx, *args: str):
    global x
    await ctx.message.delete()
    if not len(args):
        await ctx.send(
            "{mention}, you've forgotten to answer your assigned question. Try: `!accept <ANSWER>`".format(
                mention=ctx.author.mention
            )
        )
    elif args[0] in ["28", "/28", "<28>", "</28>"]:
        await ctx.author.add_roles(
            memberrole, reason="Accepted rules; Answer: " + args[0]
        )
    else:
        await ctx.send(
            "{mention}, that is not the correct answer.`".format(
                mention=ctx.author.mention
            )
        )


@bot.event
async def on_member_join(member):
    """
    Handle users joining the server.
    :param message:
    :return:
    """
    await welcomechannel.send(
        welcome_message.format(server=member.guild.name, mention=member.mention)
    )


# TODO: Enable this in a way that doesn't interfere with command processing.
# @bot.event
# async def on_message(message):
#     """
#     Handle incoming messages.
#     :param message:
#     :return:
#     """
#     if message.author == bot.user:
#         return
#
#     if message.content.startswith(command_prefix):
#         return


bot.run(token)
