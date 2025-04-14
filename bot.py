import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand

from config import config
from scheduler import HolidayScheduler
from logger import logger


class HolidayBot:
    """Telegram bot for posting daily holiday information"""
    
    def __init__(self):
        """Initialize the bot with all components"""
        # Create bot and dispatcher
        self.bot = Bot(token=config.BOT_TOKEN)
        self.dp = Dispatcher()
        
        # Create scheduler
        self.scheduler = HolidayScheduler(self.bot)
        
        # We'll set up commands later in the start method
    
    async def setup_commands(self):
        """Set up bot commands for display in Telegram interface"""
        commands = [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Получить справку"),
            BotCommand(command="post_now", description="Запостить информацию о праздниках сейчас")
        ]
        await self.bot.set_my_commands(commands)
    
    def register_handlers(self):
        """Register message handlers"""
        # Start command handler
        @self.dp.message(Command("start"))
        async def start_command(message: types.Message):
            await message.answer(
                "👋 Привет! Я бот, который публикует информацию о праздниках и "
                "знаменательных датах каждый день в 10:00.\n\n"
                "Используй /help для получения дополнительной информации."
            )
        
        # Help command handler
        @self.dp.message(Command("help"))
        async def help_command(message: types.Message):
            await message.answer(
                "🤖 <b>Справка по боту</b>\n\n"
                "Этот бот ежедневно в 10:00 публикует информацию о праздниках и "
                "знаменательных датах в канале.\n\n"
                "<b>Доступные команды:</b>\n"
                "/start - Запустить бота\n"
                "/help - Получить эту справку\n"
                "/post_now - Запостить информацию о праздниках прямо сейчас\n\n"
                "Бот использует YandexGPT для получения информации о праздниках и "
                "публикует её в заданном канале.",
                parse_mode="HTML"
            )
        
        # Post now command handler
        @self.dp.message(Command("post_now"))
        async def post_now_command(message: types.Message):
            await message.answer("🔄 Запускаю публикацию информации о праздниках...")
            await self.scheduler.post_now()
            await message.answer("✅ Задача выполнена!")
    
    async def start(self):
        """Start the bot and scheduler"""
        try:
            # Register handlers
            self.register_handlers()
            
            # Setup commands
            await self.setup_commands()
            
            # Start the scheduler
            self.scheduler.start()
            
            # Log successful start
            logger.info("Bot and scheduler started successfully")
            
            # Start polling
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.exception(f"Error starting bot: {str(e)}")
    
    async def stop(self):
        """Stop the bot and related services"""
        # Close bot session
        await self.bot.session.close()
        
        logger.info("Bot stopped")
