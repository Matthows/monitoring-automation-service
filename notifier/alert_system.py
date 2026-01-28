import requests
import logging

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Basic logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Notifier")

class AlertSystem:
    def __init__(self, telegram_token=None, chat_id=None):
        # Use passed values or fallback to environment variables
        self.telegram_token = telegram_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        # Threshold configurable via .env
        env_threshold = os.getenv("ALERT_THRESHOLD")
        self.threshold_temp = float(env_threshold) if env_threshold else 30.0

    def check_and_alert(self, data: dict):
        """
        Checks data and sends a notification if thresholds are exceeded.
        """
        temp = data.get("temperature")
        device = data.get("device_id")

        if temp and temp > self.threshold_temp:
            message = f"⚠️ ALERT: High temperature detected! Device: {device}, Value: {temp}°C"
            logger.warning(message)
            self.send_telegram(message)

    def send_telegram(self, message):
        """
        Simulates sending or actually sends if tokens are configured.
        """
        if self.telegram_token and self.chat_id:
            try:
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                response = requests.post(url, data={"chat_id": self.chat_id, "text": message})
                if response.status_code == 200:
                    logger.info(f"📤 [Telegram Sent]: {message}")
                else:
                    logger.error(f"❌ [Telegram Error] {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"❌ [Telegram Exception]: {e}")
        else:
            logger.info(f"📧 [Email/Telegram Simulation]: {message}")
