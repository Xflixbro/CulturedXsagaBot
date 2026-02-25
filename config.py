#credit dena toh de ni dena toh mat de laadle ~ GPG
import logging
from logging.handlers import RotatingFileHandler

LOG_FILE_NAME = "bot.log"
PORT = '8000'
OWNER_ID = 6048003536
MSG_EFFECT = 5046509860389126442

# BOT CONFIGURATION
# ===========================

# Telegram API Credentials (Get from https://my.telegram.org)
API_ID = 27050683
API_HASH = "013a5c0b1f2c320b98236cf212835d59"
BOT_TOKEN = "7975216525:AAFQCGlu_55OCUAFc0M47h-ytVq9UHugjQA"

# ===========================
# DATABASE
# ===========================

# MongoDB Connection String
DATABASE_URI = "mongodb+srv://FileStoreXflixBot1:FileStoreXflixBot1@cluster0.zd123bj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
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
ADMINS = [6048003536]  # Example: [123456789, 987654321]

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
