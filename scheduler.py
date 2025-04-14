import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from config import config
from yandex_gpt import YandexGPT
from logger import logger


class HolidayScheduler:
    """Scheduler for daily holiday posts"""
    
    def __init__(self, bot):
        """Initialize scheduler
        
        Args:
            bot: Initialized Aiogram bot instance
        """
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.yandex_gpt = YandexGPT(
            api_key=config.YANDEX_API_KEY,
            folder_id=config.YANDEX_FOLDER_ID,
            model=config.GPT_MODEL
        )
        
        # Set timezone
        self.tz = timezone(config.TIMEZONE)
    
    def start(self):
        """Start the scheduler"""
        logger.info(f"Starting scheduler, set to run at {config.SCHEDULED_HOUR}:{config.SCHEDULED_MINUTE:02d} "
                    f"in {config.TIMEZONE} timezone")
        
        # Schedule the job to run daily at specified time
        self.scheduler.add_job(
            self.post_holiday_info,
            CronTrigger(
                hour=config.SCHEDULED_HOUR,
                minute=config.SCHEDULED_MINUTE,
                timezone=self.tz
            ),
            name="daily_holiday_post"
        )
        
        # Start the scheduler
        self.scheduler.start()
    
    async def post_holiday_info(self):
        """Query YandexGPT and post holiday information to the channel"""
        try:
            logger.info("Running scheduled task to post holiday information")
            
            # Get today's date in readable format
            today = datetime.now(self.tz).strftime("%d.%m.%Y")
            
            # Формируем запрос с указанием текущей даты
            prompt = f"Сегодня {today}. {config.HOLIDAY_PROMPT}"
            
            # Get holiday information from YandexGPT
            holiday_info = await self.yandex_gpt.get_holiday_info(prompt)
            
            if not holiday_info:
                logger.error("Failed to get holiday information from YandexGPT")
                # Notify about the error in the channel
                await self.bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text=f"⚠️ Не удалось получить информацию о праздниках на {today}."
                )
                return
            
            # Форматируем текст - выделяем названия праздников жирным шрифтом
            formatted_text = self._format_holiday_text(holiday_info)
            
            # Format the message
            message = f"🎉 <b>Праздники и знаменательные даты</b> 📅 {today}\n\n{formatted_text}"
            
            # Send the message to the channel
            await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=message,
                parse_mode="HTML"
            )
            
            logger.info(f"Successfully posted holiday information for {today}")
            
        except Exception as e:
            logger.exception(f"Error in scheduled task: {str(e)}")
            
    def _format_holiday_text(self, text):
        """Форматирует текст с праздниками, выделяя названия жирным шрифтом.
        
        Стратегия: ищем названия праздников и событий (обычно в начале строки или после тире/дефиса)
        и выделяем их тегом <b> для жирного шрифта.
        """
        import re
        
        # Заменяем строки вида "- Название праздника" на "- <b>Название праздника</b>"
        text = re.sub(r'[-–—•●]\s+([^\.,:;]+)', r'- <b>\1</b>', text)
        
        # Обрабатываем строки, которые начинаются с названия праздника
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Если строка содержит "праздник", "день", "дата", то скорее всего в ней есть название
            holiday_keywords = ["праздник", "день", "дата", "годовщина", "фестиваль", "памят"]
            
            # Пропускаем строки, которые уже обработаны 
            if "<b>" in line:
                formatted_lines.append(line)
                continue
                
            # Проверяем, является ли строка названием праздника
            if any(keyword.lower() in line.lower() for keyword in holiday_keywords):
                # Если есть ":" в строке, выделяем текст до двоеточия
                if ":" in line:
                    parts = line.split(":", 1)
                    line = f"<b>{parts[0]}</b>:{parts[1]}"
                # Иначе, если это короткая строка, выделяем всю её
                elif len(line.split()) < 7:
                    line = f"<b>{line}</b>"
                # Для более длинных строк, пытаемся выделить первую часть до первого знака пунктуации
                else:
                    match = re.match(r'^([^\.,:;]+)(.*)$', line)
                    if match:
                        line = f"<b>{match.group(1)}</b>{match.group(2)}"
            
            formatted_lines.append(line)
        
        return "\n".join(formatted_lines)
    
    async def post_now(self):
        """Manually trigger posting holiday information"""
        await self.post_holiday_info()
