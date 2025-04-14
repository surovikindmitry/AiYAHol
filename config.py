import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration for the bot application"""
    # Bot token from @BotFather
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Channel ID where the bot will post messages (e.g. @channel_name or -100123456789)
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    # YandexGPT API credentials
    YANDEX_API_KEY: str = os.getenv("YANDEX_API_KEY", "")
    YANDEX_FOLDER_ID: str = os.getenv("YANDEX_FOLDER_ID", "")
    
    # Timezone for scheduler (default is Moscow time)
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Moscow")
    
    # Time to send the daily message (24-hour format)
    SCHEDULED_HOUR: int = int(os.getenv("SCHEDULED_HOUR", "10"))
    SCHEDULED_MINUTE: int = int(os.getenv("SCHEDULED_MINUTE", "0"))
    
    # YandexGPT prompt
    HOLIDAY_PROMPT: str = os.getenv(
        "HOLIDAY_PROMPT", 
        "Определи, какой сегодня праздник или знаменательный день. "
        "Используй российский государственный календарь, народный календарь, "
        "православный календарь, международный календарь. "
        "Выдай список праздников и событий, каждое с новой строки, используя тире в начале строки. "
        "Названия праздников указывай максимально точно. "
        "Ответ должен быть кратким и лаконичным."
    )
    
    # YandexGPT model
    GPT_MODEL: str = os.getenv("GPT_MODEL", "yandexgpt-lite")
    
    # Check if all required configs are set
    def validate(self) -> bool:
        """Validate that all required configuration values are set."""
        required_fields = ["BOT_TOKEN", "CHANNEL_ID", "YANDEX_API_KEY", "YANDEX_FOLDER_ID"]
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True


# Create a config instance for import
config = Config()
