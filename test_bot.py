import asyncio
import signal
from aiogram import Bot
from config import config
from scheduler import HolidayScheduler
from logger import logger


async def test_post():
    try:
        logger.info("Starting test post...")
        bot = Bot(token=config.BOT_TOKEN)
        scheduler = HolidayScheduler(bot)
        
        # Test post holiday info
        # Set timeout handler
        try:
            # Set a timeout of 60 seconds for the task
            task = asyncio.create_task(scheduler.post_now())
            await asyncio.wait_for(task, timeout=60.0)  # 60 seconds timeout
            logger.info("Test post completed successfully")
        except asyncio.TimeoutError:
            logger.error("Test post timed out after 60 seconds")
        except Exception as e:
            logger.exception(f"Error in post_now: {str(e)}")
        finally:
            # Clean up
            await bot.session.close()
            logger.info("Test completed")
        
    except Exception as e:
        logger.exception(f"Error in test post: {str(e)}")

def main():
    try:
        asyncio.run(test_post())
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt")

if __name__ == "__main__":
    # Set a timeout for the entire script
    signal.alarm(90)  # 90 seconds timeout for the entire script
    try:
        main()
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        # Disable the alarm
        signal.alarm(0)