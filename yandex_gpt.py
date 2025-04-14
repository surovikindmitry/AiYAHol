import aiohttp
import json
from typing import Optional
from config import config
from logger import logger


class YandexGPT:
    """Client for YandexGPT API"""
    
    def __init__(self, api_key: str, folder_id: str, model: str = "yandexgpt-lite"):
        """Initialize YandexGPT client
        
        Args:
            api_key: YandexGPT API key
            folder_id: YandexGPT folder ID
            model: YandexGPT model to use
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.model = model
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id
        }
    
    async def get_holiday_info(self, prompt: str) -> Optional[str]:
        """Query YandexGPT to get holiday information
        
        Args:
            prompt: Text prompt to send to YandexGPT
            
        Returns:
            Response text from YandexGPT or None if failed
        """
        try:
            logger.info("Querying YandexGPT for holiday information")
            
            data = {
                "modelUri": f"gpt://{self.folder_id}/{self.model}",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.5,
                    "maxTokens": 1000
                },
                "messages": [
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.error(f"YandexGPT API returned error: {response.status}, Response: {response_text}")
                        return None
                    
                    result = await response.json()
                    
                    # Extract the text from the response
                    if "result" in result and "alternatives" in result["result"] and len(result["result"]["alternatives"]) > 0:
                        if "message" in result["result"]["alternatives"][0] and "text" in result["result"]["alternatives"][0]["message"]:
                            return result["result"]["alternatives"][0]["message"]["text"]
                    
                    logger.error(f"Unexpected YandexGPT API response format: {result}")
                    return None
                    
        except Exception as e:
            logger.exception(f"Error querying YandexGPT: {str(e)}")
            return None
