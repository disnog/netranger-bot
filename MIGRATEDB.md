# Migration Guide: discord.py 1.x to 2.x with Slash Commands

This guide covers migrating the bot from legacy prefix commands to modern slash commands.

## Prerequisites

- Python 3.10+
- Completed database migration (see netranger-db MIGRATEDB.md)
- Discord bot with required intents enabled

## Discord Developer Portal Setup

### Required Intents

Enable these in the Discord Developer Portal → Bot → Privileged Gateway Intents:

- ✅ **Server Members Intent** - Required for member tracking
- ✅ **Message Content Intent** - Required for welcome channel moderation

### Bot Permissions

Required permissions (integer: 268438534):
- Manage Roles
- Kick Members
- Send Messages
- Manage Messages
- Read Message History
- Add Reactions

### Invite URL

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=268438534&scope=bot%20applications.commands
```

Note: `applications.commands` scope is required for slash commands.

## Environment Variable Changes

### Removed Variables

| Variable | Notes |
|----------|-------|
| `COMMAND_PREFIX` | Slash commands don't use prefixes |
| `MONGO_*` | Replaced by `DB_*` (see netranger-db) |

### New Required Variable

| Variable | Description |
|----------|-------------|
| `GUILD_ID` | Discord guild ID for command sync |

### All Variables

```bash
# Required
export TOKEN=your_discord_bot_token
export GUILD_ID=your_discord_guild_id

# Database (via netranger-db)
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=netranger
export DB_PASS=your_password
export DB_NAME=netranger

# Optional - Channel names (defaults shown)
export WELCOMECHANNEL_NAME=welcome
export MEMBERCHANNEL_NAME=general
export LOGCHANNEL_NAME=cnc
export MIRRORCHANNEL_NAME=mirror

# Optional - Role names (defaults shown)
export MEMBERROLE_NAME=Members

# Optional - Email verification
export SMTP_SERVER=smtp.example.com
export SMTP_PORT=587
export SMTP_USERNAME=user
export SMTP_PASSWORD=pass
export SMTP_FROMEMAIL=bot@example.com
export SECRETKEY=your_fernet_key
```

## Command Changes

### Old Prefix Commands → New Slash Commands

| Old | New | Notes |
|-----|-----|-------|
| `$accept <answer>` | Web `/join` flow at `https://disnog.org/join` | Membership acceptance moved to web; the special `$accept eggs` path was removed |
| `$myinfo` | `/myinfo` | |
| `$ipcalc info <subnet>` | `/ipcalc subnet:<text>` | |
| `$ipcalc collision <a> <b>` | `/ipoverlap subnet1:<text> subnet2:<text>` | Renamed |
| `$sendkey <email>` | `/sendkey email:<text>` | |
| `$role org set <key>` | `/orgset key:<text>` | Simplified |
| `$role org clear` | `/orgclear` | Simplified |
| `$botinfo` | `/botinfo` | Mod only |
| *(new)* | `/lookup member:<user>` | Mod only |
| *(new)* | `/syncdb` | Admin only |

### Permission Changes

Slash commands use Discord's built-in permission system:
- `/sendkey` - Requires a completed accepted join flow (`Member`, `periphery`, or `recruiter`)
- `/orgset` - Requires a completed accepted join flow (`Member`, `periphery`, or `recruiter`)
- `/orgclear` - Requires a completed accepted join flow (`Member`, `periphery`, or `recruiter`)
- `/botinfo` - Requires "Ban Members" permission
- `/lookup` - Requires "Ban Members" permission
- `/syncdb` - Requires "Administrator" permission

### Removed Legacy Behavior

- The challenge-question `$accept` flow was removed in favor of the web `/join` flow.
- The special `$accept eggs` / persistent `!eggs` role behavior was removed.
- There is no `!eggs` replacement path in `v2dev`.

## Installation

```bash
pip install git+https://github.com/disnog/netranger-bot.git@v2dev
```

## Running

```bash
# CLI
netranger-bot

# Or as module
python -m network_ranger
```

### Docker

```bash
docker build -t netranger-bot .
docker run --env-file .env netranger-bot
```

## First Run

On first startup, the bot will:
1. Connect to the database
2. Load all cogs (command modules)
3. Sync slash commands to your guild
4. Sync existing members to the database

For current guild members, startup sync and `/syncdb` replace stored permanent
roles with the roles currently present in Discord. This preserves the main
branch behavior where current Discord role state is authoritative for members
who are still in the guild. Returning members who are not currently in the guild
keep their stored permanent roles for restoration on rejoin.

**Note**: Slash command sync may take a few minutes to propagate.

## Cog Structure

```
network_ranger/
├── __main__.py      # Entry point
├── bot.py           # Main bot class
├── config.py        # Configuration
└── cogs/
    ├── onboarding.py   # /myinfo, member events, role restoration
    ├── ipcalc.py       # /ipcalc, /ipoverlap
    ├── roles.py        # /sendkey, /orgset, /orgclear
    └── moderation.py   # /botinfo, /lookup, /syncdb
```

## Migration Checklist

- [ ] Update Discord bot with new intents
- [ ] Add `applications.commands` scope to invite URL
- [ ] Re-invite bot to server (or update permissions)
- [ ] Migrate database (see netranger-db)
- [ ] Update environment variables
- [ ] Deploy new bot version
- [ ] Verify slash commands appear (may take minutes)
- [ ] Test core functionality:
  - [ ] Web `/join` flow grants selected role before guild join
  - [ ] `/myinfo` shows profile
  - [ ] `/ipcalc 192.168.1.0/24` shows subnet info
  - [ ] New members without accepted roles are prompted to use `/join`
  - [ ] Returning members get permanent roles restored and member number retained
  - [ ] Returning `periphery` and `recruiter` users are welcomed back without being sent to `/join`
  - [ ] `/syncdb` removes stale stored roles from current members after a Discord role is removed

## Troubleshooting

### Slash commands not appearing

1. Check bot has `applications.commands` scope
2. Wait a few minutes for Discord to sync
3. Check logs for sync errors

### "Missing Access" errors

Bot needs to be re-invited with updated permissions.

### Database connection errors

Verify `DB_*` environment variables are set correctly.

### Members not being tracked

Ensure "Server Members Intent" is enabled in Discord Developer Portal.
