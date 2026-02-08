#!/usr/bin/env python3

# __main__.py
# Copyright (C) 2020-2026 DisNOG.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Entry point for the Network Ranger bot."""

import asyncio
import logging
import sys

from .bot import NetworkRanger
from .config import Config


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    
    # Reduce discord.py noise
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)


async def run_bot():
    """Run the bot."""
    config = Config.from_env()
    bot = NetworkRanger(config)
    
    async with bot:
        await bot.start(config.token)


def main():
    """CLI entry point."""
    setup_logging()
    
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
