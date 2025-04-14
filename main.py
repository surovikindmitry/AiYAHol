import asyncio
import sys
from config import config
from bot import HolidayBot
from logger import logger
from app import app  # Import Flask app


async def main():
    """Main entry point for the application"""
    # Validate configuration
    if not config.validate():
        logger.error("Invalid configuration. Please check your environment variables.")
        logger.error("Required environment variables: BOT_TOKEN, CHANNEL_ID, YANDEX_API_KEY, YANDEX_FOLDER_ID")
        sys.exit(1)
    
    # Create and start the bot
    bot = HolidayBot()
    
    try:
        logger.info("Starting YaGptHoliday bot...")
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
    finally:
        if bot:
            await bot.stop()


if __name__ == "__main__":
    # Start the event loop
    asyncio.run(main())