# netranger-bot

Discord bot for the DisNOG server. Built with discord.py 2.x using slash commands.

## Installation

```bash
pip install git+https://github.com/disnog/netranger-bot.git@v2dev
```

Or for development:

```bash
git clone https://github.com/disnog/netranger-bot.git
cd netranger-bot
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in values, or export directly:

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

# Optional — channel/role names (defaults shown)
export WELCOMECHANNEL_NAME=welcome
export MEMBERCHANNEL_NAME=general
export LOGCHANNEL_NAME=cnc
export MIRRORCHANNEL_NAME=mirror
export MEMBERROLE_NAME=Members

# Optional — email verification (all required if any are set)
export SMTP_SERVER=smtp.example.com
export SMTP_PORT=587
export SMTP_USERNAME=user
export SMTP_PASSWORD=pass
export SMTP_FROMEMAIL=bot@example.com
export SECRETKEY=your_fernet_key  # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
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
| `/myinfo` | Show your member profile | Everyone |
| `/ipcalc <subnet>` | Calculate IP subnet info | Everyone |
| `/ipoverlap <subnet1> <subnet2>` | Check if subnets overlap | Everyone |
| `/sendkey <email>` | Send email verification key | Accepted members |
| `/orgset <key>` | Set org affiliation role | Accepted members |
| `/orgclear` | Remove org affiliation | Accepted members |
| `/botinfo` | Show bot information | Moderators |
| `/lookup <member>` | Look up member database info | Moderators |
| `/syncdb` | Force sync members to database | Admins |

## Features

- **Member onboarding**: Welcome messages plus `/join` guidance for unaccepted users
- **Returning members**: Remembers member numbers and roles across leave/rejoin
- **IP Calculator**: Subnet calculations and overlap checking
- **Org verification**: Email-based organization affiliation roles

Removed in `v2dev`: the legacy `$accept eggs` / persistent `!eggs` flow. There is no replacement path for `!eggs`.

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

## Development

### Setup

```bash
git clone https://github.com/disnog/netranger-bot.git
cd netranger-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env   # edit with real values
```

### Running Tests

Tests use `pytest-asyncio` and mock the Discord API and database — **no live bot token or database is required**.

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest -v --cov=network_ranger --cov-report=term-missing

# Run a specific test file
pytest tests/test_cogs_ipcalc.py -v
```

### Linting

```bash
ruff check .
ruff check . --fix   # auto-fix safe issues
```

## License

GPL-3.0-or-later
