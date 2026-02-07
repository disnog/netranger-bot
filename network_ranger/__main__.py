#!/usr/bin/env python3
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
