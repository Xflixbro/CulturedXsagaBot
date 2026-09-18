#credit dena toh de ni dena toh mat de laadle ~ GPG
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE_NAME = "bot.log"
PORT = '8000'
OWNER_ID = 8741514787
MSG_EFFECT = 5046500389126442

# BOT CONFIGURATION
# ===========================

# Telegram API Credentials (Get from https://my.telegram.org)
API_ID = 39185942
API_HASH = "36bb0447e7986c4a81e17b7281980b44"
BOT_TOKEN = ""

# ===========================
# DATABASE
# ===========================

# MongoDB Connection String
DATABASE_URI = ""
DATABASE_NAME = "OFLIX"

# ===========================
# CHANNELS
# ===========================

# Main Database Channel ID (where files are stored)
DB_CHANNEL = -1002162795137

# Force Subscribe Channels (users must join these)
FORCE_SUB_CHANNELS = []  # Example: [-1001234567890, -1009876543210]

# ===========================
# ADMIN
# ===========================

# Admin User IDs (can use admin commands)
ADMINS = [6048003536, 821215952, 8365451390]

# ===========================
# SERVER (Optional)
# ===========================

# Use webhook instead of polling
WEBHOOK = False

# CUSTOMIZATION (Optional)
# ===========================

# Auto delete timer (seconds, 0 to disable)
AUTO_DELETE = 300

# Protect content (prevent forwarding)
PROTECT_CONTENT = False

# Disable share button
DISABLE_BUTTON = False

# AroLinks URL Shortener Configuration
AROLINKS_API_TOKEN = "d5911095597018fad72bf9ad1df544163b1520db"
AROLINKS_API_URL = "https://shortxlinks.com"

# URL Shortener Providers Configuration
URL_SHORTENERS = {
    'arolinks': {
        'name': 'Shortxlinks',
        'api_url': 'https://shortxlinks.com/api',
        'api_token': AROLINKS_API_TOKEN,
        'format': 'text',
        'active': True
    }
}

# BYPASS ATTEMPT MEDIA
# ===========================
BYPASS_ATTEMPT_MEDIA = "https://videotourl.com/videos/1788160021118-5b825ba1-c273-4df3-9c10-1649b6c73ee7.mp4 https://i.postimg.cc/4ykP3SHc/IMG-20250927-131101-178.jpg"

MYPLAN_IMG = "https://i.postimg.cc/L6D7Vzcm/46Lv-Lz-MD19tzyo-Pc7HUf4PPvi62.jpg"

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
