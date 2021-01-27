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

import asyncio
import json
import os
import sys
from datetime import datetime

import classes
import discord
import send_email
import subnet_calc
from cogs.background_timer import BackgroundTimer
from cryptography.fernet import Fernet, InvalidToken
from db import Db
from discord.ext import commands
from email_validator import validate_email, EmailNotValidError
import re
import random

conf = classes.Config()

if conf.get("db_name") and conf.get("db_user"):
    db = Db(
        host=conf.get("db_host"),
        port=int(conf.get("db_port")),
        mongo_user=conf.get("db_user"),
        mongo_pass=conf.get("db_pass"),
        dbname=conf.get("db_name"),
    )
else:
    db = False
    print("DB configuration not present; not attempting to connect to DB.")

bot = commands.Bot(
    command_prefix=conf.get("command_prefix"),
    description=conf.get("bot_description"),
    activity=discord.Activity(
        type=discord.ActivityType.playing,
        name="Network Ranger | {}help".format(conf.get("command_prefix")),
        url="https://github.com/Networking-discord/network-ranger",
    ),
)

bot.add_cog(BackgroundTimer(bot))

async def clear_member_roles(member, roletype: str):
    for role in member.roles:
        if role.name.startswith(roletype + ":"):
            await member.remove_roles(role)
            if len(role.members) == 0:
                await role.delete(reason="Last member removed from dynamic role.")


# Define predicates for bot commands checks
async def is_guild_admin(ctx):
    return ctx.author.guild_permissions.administrator


async def is_guild_mod(ctx):
    return ctx.author.guild_permissions.ban_members


async def is_not_accepted(ctx):
    return memberrole not in ctx.author.roles


async def is_accepted(ctx):
    return memberrole in ctx.author.roles


async def process_noncommands(message):
    if message.channel is welcomechannel:
        embed = discord.Embed()
        embed.add_field(name="User", value=message.author.name)
        embed.add_field(name="Message", value=message.clean_content)
        await mirrorchannel.send(embed=embed)
        if not message.author.bot and not await is_guild_admin(message):
            await message.delete()


@bot.event
async def on_ready():
    print(
        'Logged in as "{username}" (ID: {userid})'.format(
            username=bot.user.name, userid=bot.user.id
        )
    )
    if db:
        db.add_existing_members(bot.guilds[0])

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
    global eggsrole
    eggsrole = discord.utils.get(
        welcomechannel.guild.roles, name=conf.get("eggsrole_name")
    )
    print(
        "Member Role: {eggsrole_name} (ID: {eggsrole_id})".format(
            eggsrole_name=eggsrole.name, eggsrole_id=eggsrole.id
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


@bot.command(help="Shows bot information")
@commands.check(is_guild_mod)
async def botinfo(ctx):
    embed = discord.Embed(
        title="Network Ranger", description=conf.get("bot_description")
    )
    embed.add_field(name="Host", value=os.uname()[1])
    embed.add_field(name="Command Prefix", value=conf.get("command_prefix"))
    embed.add_field(
        name="Github", value="https://github.com/networking-discord/network-ranger"
    )
    await ctx.send(embed=embed)


@bot.command(help="Shows your member profile")
@commands.check(is_accepted)
async def myinfo(ctx):
    embed = discord.Embed(
        title=ctx.author.display_name,
        description=f"{ctx.author.name}#{ctx.author.discriminator}",
    )
    member_info = db.get_member(ctx.author.id)
    embed.add_field(name="Member Number", value=member_info["member_number"])
    embed.add_field(
        name="First Joined At",
        value=datetime.utcfromtimestamp(member_info["first_joined_at"]).strftime(
            "%Y-%b-%d %H:%M:%S UTC"
        ),
    )
    permanent_roles = "\r\n".join(db.get_permanent_roles(ctx.author.id))
    embed.add_field(name="Permanent Roles", value=permanent_roles)
    await ctx.send(embed=embed)


@bot.command(help="Send an email key")
@commands.check(is_accepted)
async def sendkey(ctx, email: str):
    # Delete the message if it hasn't already been deleted.
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass
    except discord.errors.Forbidden:
        pass
    # Validate the email address.
    if email == None:
        await ctx.send(
            "{mention}: You must specify the email address.".format(
                mention=ctx.author.mention
            )
        )
        return
    try:
        valid = validate_email(email)
        email = valid.email
        domain = valid.domain
        secretkey = conf.get("secretkey").encode()
        # Calculate an encrypted JSON string with userid and email
        emailkey = json.dumps({"uid": str(ctx.author.id), "email": email})
        emailkey = Fernet(secretkey).encrypt(emailkey.encode())
        msg = """\
To: {email}
Subject: Networking Discord Email Validation Key

Your validation key is {key}. To activate an org affiliation role, in the server, please issue the command:
{command_prefix}role org set {key}

Note that doing so will remove your present org affiliation role, if any.
""".format(
            email=email,
            key=emailkey.decode(),
            command_prefix=conf.get("command_prefix"),
        )
        await send_email.send_email(email, msg)
        await ctx.send(
            "{mention}: I've emailed you to check your association with {domain}. "
            "Please check your email for the validation instructions.".format(
                domain=domain, mention=ctx.author.mention
            )
        )
    except EmailNotValidError as e:
        await ctx.send(str(e))


@bot.group(help="Set or clear roles for yourself")
@commands.check(is_accepted)
async def role(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "{mention}: Invalid subcommand.".format(mention=ctx.author.mention)
        )


@role.group(help="Modify org information")
async def org(ctx):
    # Delete the message if it hasn't already been deleted.
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "{mention}: Invalid subcommand.".format(mention=ctx.author.mention)
        )


@org.command(help="Clear your org affiliation role.")
async def clear(ctx):
    await clear_member_roles(ctx.author, "org")
    await ctx.send(
        "{mention}: Your org (if any) has been cleared.".format(
            mention=ctx.author.mention
        )
    )


@org.command(help="Set an org affiliation role using your email verification key.")
async def set(ctx, key: str = None):
    if key == None:
        await ctx.send(
            "{mention}: You must specify the email verification key. If you do not yet have your email "
            "verification key, use `{command_prefix}sendkey <email>` to get your key.".format(
                mention=ctx.author.mention
            )
        )
        return
    try:
        # Decrypt the email key}
        salt = str(ctx.author.id).encode()
        secretkey = conf.get("secretkey").encode()
        emailkey = Fernet(secretkey).decrypt(key.encode()).decode()
        emailkey = str(emailkey)
        emailkey = json.loads(emailkey)
        if (
            "uid" not in emailkey
            or "email" not in emailkey
            or emailkey["uid"] != str(ctx.author.id)
        ):
            await ctx.send("{mention}: Invalid key".format(mention=ctx.author.mention))
            raise Exception("Invalid emailkey", emailkey)
        valid = validate_email(emailkey["email"])
        domain = valid.domain
        await clear_member_roles(ctx.author, "org")

        # Find the role
        newrole = discord.utils.find(
            lambda r: r.name == "org:{domain}".format(domain=domain), ctx.guild.roles
        )

        # If the role doesn't exist, create it
        if newrole == None:
            newrole = await ctx.guild.create_role(
                name="org:{domain}".format(domain=domain)
            )
        await ctx.author.add_roles(newrole)

        await ctx.send(
            "{mention}: Your org affiliation has been set to {domain}".format(
                domain=domain, mention=ctx.author.mention
            )
        )
    except InvalidToken:
        await ctx.send("{mention}: Invalid key".format(mention=ctx.author.mention))
    except EmailNotValidError as e:
        await ctx.send(str(e))


@bot.group(help="IP Subnet Calculator")
@commands.check(is_accepted)
async def ipcalc(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "{mention}: Invalid subcommand.".format(mention=ctx.author.mention)
        )


@ipcalc.command(help="Display info on an IP subnet", aliases=["ipc", "subnetinfo"])
async def info(ctx, *args: str):
    if not len(args):
        await ctx.send(
            "{mention}, this command requires an argument.".format(
                mention=ctx.author.mention, command_prefix=conf.get("command_prefix")
            )
        )
        return
    subnet_calc.argumentList = args
    result = subnet_calc.subnet_calc_function()

    embed = discord.Embed(title="IP Calculator", description="Standard IP Subnet Calc")
    embed.add_field(name="User", value=ctx.author.mention)
    embed.add_field(
        name="Question",
        value="{}".format(
            discord.utils.escape_markdown(discord.utils.escape_mentions(" ".join(args)))
        ),
    )
    embed.add_field(name="Answer", value=result, inline=False)

    if result:
        await ctx.send(embed=embed)
    elif not result:
        await ctx.send("`Something went wrong, contact a Mod.`")


@ipcalc.command(help="Check if two IP subnets overlap", aliases=["overlap", "cc"])
async def collision(ctx, *args: str):
    if not len(args):
        await ctx.send(
            "{mention}, this command requires an argument.".format(
                mention=ctx.author.mention, command_prefix=conf.get("command_prefix")
            )
        )
        return
    subnet_calc.argumentList = args
    result = subnet_calc.subnet_collision_checker_function()

    embed = discord.Embed(
        title="IP Calculator", description="IP Subnet Collision check feature"
    )
    embed.add_field(name="User", value=ctx.author.mention)
    embed.add_field(
        name="Question",
        value="{}".format(
            discord.utils.escape_markdown(discord.utils.escape_mentions(" ".join(args)))
        ),
    )
    embed.add_field(name="Answer", value=result, inline=False)

    if result:
        await ctx.send(embed=embed)
    elif not result:
        await ctx.send("`Something went wrong, contact a Mod.`")


@bot.command(
    help="Answer the challenge question in #{}".format(conf.get("welcomechannel_name"))
)
@commands.check(is_not_accepted)
async def accept(ctx, answer: str = None):
    if answer != None:
        # Strip special characters from the answer
        answer = re.sub(r"\W", "", answer)
    if answer == None:
        await ctx.send(
            "*****{mention}, you've forgotten to answer your assigned question. Try: `{command_prefix}accept <ANSWER>`".format(
                mention=ctx.author.mention, command_prefix=conf.get("command_prefix")
            )
        )
    elif answer.lower() in ["tcp"]:
        await ctx.author.add_roles(
            memberrole, reason="Accepted rules; Answer: " + answer
        )
        db.add_permanent_role(ctx.author.id, "Member")
        db.add_member_numbers()
        await memberchannel.send(
            "{mention}, welcome to {server}! You are member #{membernumber}, and we're glad to have you. Feel free to "
            "take a moment to introduce yourself!".format(
                mention=ctx.author.mention,
                server=memberchannel.guild.name,
                membernumber=db.get_member_number(ctx.author.id),
                command_prefix=conf.get("command_prefix"),
            )
        )
    elif answer == "eggs":
        await ctx.author.add_roles(
            eggsrole, reason="Really, terribly, desperately addicted to eggs."
        )
        db.add_permanent_role(ctx.author.id, "!eggs")
        response = (
            "*****{mention}, congratulations! You've joined {eggsmention}! For more information about eggs, please "
            "visit https://lmgtfy.com/?q=eggs or consult your local farmer.".format(
                mention=ctx.author.mention, eggsmention=eggsrole.mention
            )
        )
        message = await ctx.send(response)
        await message.add_reaction("\U0001F973")
    else:
        await ctx.send(
            "*****{mention}, that is not the correct answer. Please try again once the timer allows.".format(
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
    db.add_member(member)
    permanent_roles = db.get_permanent_roles(member.id)
    if "!eggs" in permanent_roles:
        # Reapply !eggs role if they had it before
        await member.add_roles(eggsrole, reason="Eggs have returned.")
    if "Member" in permanent_roles:
        # Bypass welcome channel
        await member.add_roles(memberrole)
        await memberchannel.send(
            "{mention}, welcome back to {server}! We've held on to your previous member number,"
            " #{membernumber}.".format(
                mention=member.mention,
                server=memberchannel.guild.name,
                membernumber=db.get_member_number(member.id),
            )
        )
    else:
        # Send to welcome channel
        db.add_first_joined_ats(bot.guilds[0])
        await welcomechannel.send(
            conf.get("welcomemessage").format(
                server=member.guild.name,
                mention=member.mention,
                command_prefix=conf.get("command_prefix"),
            )
        )


@bot.event
async def on_message(message):
    """
    Handle incoming messages.
    :param message:
    :return:
    """
    # Don't do anything if the author is the bot itself unless the message content starts with "*****"
    if message.author == bot.user and not message.clean_content.startswith("*****"):
        return
    # Process messages that aren't issued as commands
    await asyncio.create_task(process_noncommands(message))
    # Process commands using the discord.py bot module
    await asyncio.create_task(bot.process_commands(message))


if __name__ == "__main__":

    token: str = conf.get("token")
    if token is None:
        print("Fatal: Discord bot token not set. Exiting")
        sys.exit(1)
    try:
        bot.run(token)
    except discord.errors.LoginFailure as login_failure:
        sys.exit(str(login_failure))
