# netranger-bot

Discord bot for the DisNOG server. Built with discord.py 2.x using slash commands.

## Installation

```bash
pip install git+https://github.com/disnog/netranger-bot.git
```

Or for development:

```bash
git clone https://github.com/disnog/netranger-bot.git
cd netranger-bot
pip install -e .
```

## Configuration

Set environment variables:

```bash
# Required
export TOKEN=your_discord_bot_token
export GUILD_ID=your_discord_guild_id

# Database (via netranger-db)
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=netranger
export DB_PASS=secret
export DB_NAME=netranger

# Optional - Channel/Role names (defaults shown)
export WELCOMECHANNEL_NAME=welcome
export MEMBERCHANNEL_NAME=general
export LOGCHANNEL_NAME=cnc
export MIRRORCHANNEL_NAME=mirror
export MEMBERROLE_NAME=Members
export EGGSROLE_NAME=!eggs

# Optional - Email verification
export SMTP_SERVER=smtp.example.com
export SMTP_PORT=587
export SMTP_USERNAME=user
export SMTP_PASSWORD=pass
export SMTP_FROMEMAIL=bot@example.com
export SECRETKEY=your_fernet_key  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Running

```bash
netranger-bot
# or
python -m network_ranger
```

### Docker

```bash
docker build -t netranger-bot .
docker run --env-file .env netranger-bot
```

## Slash Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/accept <answer>` | Accept rules and become a member | Everyone |
| `/myinfo` | Show your member profile | Everyone |
| `/ipcalc <subnet>` | Calculate IP subnet info | Everyone |
| `/ipoverlap <subnet1> <subnet2>` | Check if subnets overlap | Everyone |
| `/sendkey <email>` | Send email verification key | Everyone |
| `/orgset <key>` | Set org affiliation role | Everyone |
| `/orgclear` | Remove org affiliation | Everyone |
| `/botinfo` | Show bot information | Moderators |
| `/lookup <member>` | Look up member database info | Moderators |
| `/syncdb` | Force sync members to database | Admins |

## Features

- **Member onboarding**: Welcome messages, challenge question, automatic role assignment
- **Returning members**: Remembers member numbers and roles across leave/rejoin
- **IP Calculator**: Subnet calculations and overlap checking
- **Org verification**: Email-based organization affiliation roles
- **Auto-pruning**: Kicks members who don't accept rules within 72 hours
- **Easter eggs**: 🥚

## Bot Permissions

Required Discord permissions:
- Manage Roles
- Manage Channels (for creating org roles)
- Send Messages
- Read Message History
- Kick Members

Required Intents:
- Server Members Intent
- Message Content Intent

## License

GPL-3.0-or-later
