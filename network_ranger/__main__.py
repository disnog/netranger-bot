#!/usr/bin/config python3

#  network_ranger - __main__.py
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
Discord bot to maintain the Networking Discord Server.
"""

import discord
from discord.ext import commands
import classes
from datetime import datetime
import asyncio

conf = classes.Config()

bot = commands.Bot(
    command_prefix=conf.get("command_prefix"),
    description=conf.get("bot_description"),
    # TODO: De-hardcode activity
    activity=discord.Activity(
        type=discord.ActivityType.playing,
        name="Network Ranger",
        url="https://github.com/Networking-discord/network-ranger",
    ),
)

# Define predicates for bot commands checks
async def is_guild_admin(ctx):
    return ctx.author.guild_permissions.administrator


async def is_guild_mod(ctx):
    return ctx.author.guild_permissions.ban_members


async def is_not_accepted(ctx):
    return memberrole not in ctx.author.roles


async def is_accepted(ctx):
    return memberrole in ctx.author.roles


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
        bot.get_all_channels(),
        guild__name=conf.get("guild_name"),
        name=conf.get("welcomechannel_name"),
    )
    print(
        "Welcome Channel: {welcomechannel_name} (ID: {welcomechannel_id})".format(
            welcomechannel_name=welcomechannel.name, welcomechannel_id=welcomechannel.id
        )
    )
    global memberrole
    memberrole = discord.utils.get(
        welcomechannel.guild.roles, name=conf.get("memberrole_name")
    )
    print(
        "Member Role: {memberrole_name} (ID: {memberrole_id})".format(
            memberrole_name=memberrole.name, memberrole_id=memberrole.id
        )
    )
    global memberchannel
    memberchannel = discord.utils.get(
        bot.get_all_channels(),
        guild__name=conf.get("guild_name"),
        name=conf.get("memberchannel_name"),
    )
    print(
        "Member Channel: {memberchannel_name} (ID: {memberchannel_id})".format(
            memberchannel_name=memberchannel.name, memberchannel_id=memberchannel.id
        )
    )
    global logchannel
    logchannel = discord.utils.get(
        bot.get_all_channels(),
        guild__name=conf.get("guild_name"),
        name=conf.get("logchannel_name"),
    )
    print(
        "Log Channel: {logchannel_name} (ID: {logchannel_id})".format(
            logchannel_name=logchannel.name, logchannel_id=logchannel.id
        )
    )
    global mirrorchannel
    mirrorchannel = discord.utils.get(
        bot.get_all_channels(),
        guild__name=conf.get("guild_name"),
        name=conf.get("mirrorchannel_name"),
    )
    print(
        "Mirror Channel: {mirrorchannel_name} (ID: {mirrorchannel_id})".format(
            mirrorchannel_name=mirrorchannel.name, mirrorchannel_id=mirrorchannel.id
        )
    )
    await logchannel.send(
        "Bot Online. Command prefix: {command_prefix}".format(
            command_prefix=conf.get("command_prefix")
        )
    )
    # Build a list of members to kick if they've been sitting in the welcome channel more than 7 days.
    members_to_prune = list()
    for member in welcomechannel.members:
        if (
            memberrole not in member.roles
            and (datetime.now() - member.joined_at).days >= 3
            and not member.bot
        ):
            members_to_prune.append(member)
    await welcomechannel.send(
        "I'll soon prune the following non-members lingering > 3 days unless they accept: {}".format(
            [
                (member.mention, str((datetime.now() - member.joined_at).days) + "days")
                for member in members_to_prune
            ]
        )
    )


@bot.command(help="Shows bot information")
@commands.check(is_guild_mod)
async def info(ctx):
    embed = discord.Embed(
        title="Network Ranger", description=conf.get("bot_description")
    )
    embed.add_field(name="Command Prefix", value=conf.get("command_prefix"))
    embed.add_field(
        name="Github", value="https://github.com/networking-discord/network-ranger"
    )
    await ctx.send(embed=embed)


@bot.command(
    help="Answer the challenge question in #{}".format(conf.get("welcomechannel_name"))
)
@commands.check(is_not_accepted)
async def accept(ctx, *args: str):
    if not len(args):
        await ctx.send(
            "{mention}, you've forgotten to answer your assigned question. Try: `{command_prefix}accept <ANSWER>`".format(
                mention=ctx.author.mention, command_prefix=conf.get("command_prefix")
            )
        )
    elif args[0] in ["28", "/28", "<28>", "</28>"]:
        await ctx.author.add_roles(
            memberrole, reason="Accepted rules; Answer: " + args[0]
        )
        await memberchannel.send(
            "{mention}, welcome to {server}! You are member #{membernumber}, and we're glad to have you. Feel free to take a moment to introduce yourself!".format(
                mention=ctx.author.mention,
                server=memberchannel.guild.name,
                membernumber=len(memberrole.members),
            )
        )
    else:
        await ctx.send(
            "{mention}, that is not the correct answer. Please try again once the timer allows.".format(
                mention=ctx.author.mention
            )
        )


@bot.event
async def on_member_join(member):
    """
    Handle users joining the server.
    :param member:
    :return:
    """
    await welcomechannel.send(
        conf.get("welcomemessage").format(
            server=member.guild.name,
            mention=member.mention,
            command_prefix=conf.get("command_prefix"),
        )
    )


# TODO: Enable this in a way that doesn't interfere with command processing.
@bot.event
async def on_message(message):
    """
    Handle incoming messages.
    :param message:
    :return:
    """
    await asyncio.create_task(bot.process_commands(message))
    if message.author == bot.user:
        return

    if message.channel is welcomechannel:
        embed = discord.Embed()
        embed.add_field(name="User", value=message.author.name)
        embed.add_field(name="Message", value=message.clean_content)
        await mirrorchannel.send(embed=embed)
        await message.delete()


bot.run(conf.get("token"))
