#credit dena toh de ni dena toh mat de laadle ~ GPG
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE_NAME = "bot.log"
PORT = '8000'
OWNER_ID = 8741514787
MSG_EFFECT = 5046509860389126442

# BOT CONFIGURATION
# ===========================

# Telegram API Credentials (Get from https://my.telegram.org)
API_ID = 39185942
API_HASH = "36bb0447e7986c4a81e17b7281980b44"
BOT_TOKEN = "8955831474:AAFzk-lSjJcje1ZJ5hgoFceCFSs4AMj4Xdk"

# ===========================
# DATABASE
# ===========================

# MongoDB Connection String
DATABASE_URI = "mongodb+srv://eonxfstBotv1:eonxfstBotv1@cluster0.qpkmqq8.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "CORNXVILLA"

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
ADMINS = [6048003536, 821215952, 8365451390]  # Example: [123456789, 987654321]

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


# VPLink URL Shortener Configuration
VPLINK_API_TOKEN = "akenamebepuresososebandhadhaga"
VPLINK_API_URL = "example.com"

# URL Shortener Providers Configuration
URL_SHORTENERS = {
    'vplink': {
        'name': 'VPLink',
        'api_url': 'https://vplink.in/api',
        'api_token': VPLINK_API_TOKEN,
        'format': 'text',
        'active': True
    }
}

# ===========================
# PERMANENT LINK SYSTEM
# ===========================

# Permanent Link System - Works even if bot gets banned
PERMANENT_LINKS = os.environ.get("PERMANENT_LINKS", "True") == "True"
WEBSITE_URL = os.environ.get("WEBSITE_URL", "https://xsagavercal.vercel.app/")
WEBSITE_PARAM = os.environ.get("WEBSITE_PARAM", "Neostart2")

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
