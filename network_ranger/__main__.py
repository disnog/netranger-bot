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
import subnet_calc
import smtplib, ssl
import hashlib
from email_validator import validate_email, EmailNotValidError

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


async def send_email(to_email, message):
    smtp_server = conf.get("smtp_server")
    port = conf.get("smtp_port")
    username = conf.get("smtp_username")
    password = conf.get("smtp_password")
    from_email = conf.get("smtp_fromemail")
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)
        server.login(username, password)
        server.sendmail(from_email, to_email, message)
    except Exception as e:
        print(e)
    finally:
        server.quit()


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


async def prune_non_members():
    # Build a list of members to kick if they've been sitting in the welcome channel more than 3 days.
    warning_seconds = 172800
    kick_seconds = 259200
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
                        command_prefix=conf.get("command_prefix"),
                    )
                )
            if time_on_server.total_seconds() > kick_seconds:
                # Kick the user for not accepting.
                try:
                    await member.send(
                        "You are being removed from {server} because you have not accepted the rules. We'd still love"
                        " to have you if you're interested in network engineering. If you wish to rejoin, please feel"
                        " free to do so using the join link at {url}.".format(
                            server=conf.get("guild_name"),
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


async def every_minute():
    while True:
        await asyncio.create_task(prune_non_members())
        await asyncio.sleep(60)


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
    # Start routine maintenance timer
    await asyncio.create_task(every_minute())


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


@bot.group(help="Change user profile information")
@commands.check(is_accepted)
async def profile(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "{mention}: Invalid subcommand.".format(mention=ctx.author.mention)
        )


@profile.group(help="Modify org information")
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


@org.command(help="Set an org affiliation role.")
async def set(ctx, email: str = None):
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
        # Calculate a hashed key based on the static salt in the config, the user's unique Discord ID, and the email.
        hashedvalue = hashlib.sha1(
            (conf.get("staticsalt") + str(ctx.author.id) + email).encode()
        ).hexdigest()
        msg = """\
To: {email}
Subject: Org Validation Key

Your validation key is {key}. To activate your org affiliation, please send me the command:
{command_prefix}profile org confirm {email} {key}

Note that doing so will remove your present affiliation, if any.
""".format(
            email=email, key=hashedvalue, command_prefix=conf.get("command_prefix")
        )
        await send_email(email, msg)
        await ctx.send(
            "{mention}: I've emailed you to check your association with {domain}. Please check your email for the validation instructions.".format(
                domain=domain, mention=ctx.author.mention
            )
        )
    except EmailNotValidError as e:
        await ctx.send(str(e))


@org.command(help="Clear your org affiliation role.")
async def clear(ctx):
    await clear_member_roles(ctx.author, "org")
    await ctx.send(
        "{mention}: Your org (if any) has been cleared.".format(
            mention=ctx.author.mention
        )
    )


@org.command(help="Confirm an org affiliation role using the key from your email.")
async def confirm(ctx, email: str = None, key: str = None):
    if key == None:
        await ctx.send(
            "{mention}: You must specify the email address and verification key.".format(
                mention=ctx.author.mention
            )
        )
        return
    try:
        valid = validate_email(email)
        email = valid.email
        domain = valid.domain
        hashedvalue = hashlib.sha1(
            (conf.get("staticsalt") + str(ctx.author.id) + email).encode()
        ).hexdigest()
        if key == hashedvalue:
            await clear_member_roles(ctx.author, "org")

            # Find the role
            newrole = discord.utils.find(
                lambda r: r.name == "org:{domain}".format(domain=domain),
                ctx.guild.roles,
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
        else:
            await ctx.send("{mention}: Invalid key.".format(mention=ctx.author.mention))
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
    if answer == None:
        await ctx.send(
            "*****{mention}, you've forgotten to answer your assigned question. Try: `{command_prefix}accept <ANSWER>`".format(
                mention=ctx.author.mention, command_prefix=conf.get("command_prefix")
            )
        )
    elif answer in ["28", "/28", "<28>", "</28>"]:
        await ctx.author.add_roles(
            memberrole, reason="Accepted rules; Answer: " + answer
        )
        await memberchannel.send(
            "{mention}, welcome to {server}! You are member #{membernumber}, and we're glad to have you. Feel free to take a moment to introduce yourself!".format(
                mention=ctx.author.mention,
                server=memberchannel.guild.name,
                membernumber=len(memberrole.members),
            )
        )
    elif answer == "eggs":
        await ctx.author.add_roles(
            eggsrole, reason="Really, terribly, desperately addicted to eggs."
        )
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


bot.run(conf.get("token"))
