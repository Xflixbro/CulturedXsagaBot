<p align="center">
  <img src="https://i.ibb.co/gbVyYG8z/photo-2026-02-17-18-28-50-7607902977038221336.jpg" alt="Advanced File Store Bot Banner" width="100%">
</p>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Montserrat&weight=700&size=28&pause=1200&color=00BFFF&center=true&vCenter=true&width=750&lines=Advanced+File+Sharing+Bot;Premium+%7C+Multi-DB+%7C+Batch+System;Powered+by+Awakeners+Bots" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Awakener_bots/File-Store?style=for-the-badge&color=00BFFF">
  <img src="https://img.shields.io/github/forks/Awakener_bots/File-Store?style=for-the-badge&color=00BFFF">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/MongoDB-Database-green?style=for-the-badge">
</p>

---

# Telegram File Sharing Bot

A powerful Telegram bot for file sharing with advanced features including batch processing, premium memberships, multi-database channel support, URL shortening with token verification, and comprehensive admin controls.

---

## ✨ Features

### Core Features
- 📁 **File Sharing** - Share files via unique links with automatic link generation
- 🔒 **Hybrid Token System** - Secure, random 12-16 char token links with full backward compatibility for legacy Base64 links.
- 📦 **Batch Processing** - Create batches for episodes/seasons with cancel functionality
- 🤖 **Auto Batch** - Automatic batch creation with quality detection and configurable time windows
- 💎 **Premium System** - Full subscription management with pricing tiers and expiry tracking
- 🗄️ **Multi-DB Channels** - Round-robin file distribution across multiple database channels
- 🔗 **URL Shortening** - Integrated URL shortener with multiple provider support

### Admin Features
- 👥 **Premium User Management** - Control panel to add/remove premium users with expiry dates
- 📊 **Statistics Dashboard** - Track bot usage, user stats, and premium subscriptions
- 🔒 **Force Subscribe** - Require channel subscription for file access
- 💳 **Credit System** - Token-based access control with package management
- 🔐 **Security Panel** - Token verification, anti-bypass protection, and bypass logs
- 📢 **Broadcast System** - Send messages to all users or specific groups

### User Experience
- 🎨 **Modern UI** - Small caps font styling with blockquotes for premium look
- ⚡ **Fast Performance** - Optimized file delivery and caching
- 🔔 **Notifications** - Auto-notify users on premium status changes
- 📱 **Mobile Friendly** - Responsive design for all devices

---

## 📋 Requirements

- Python 3.8+
- MongoDB
- Telegram Bot Token (from @BotFather)
- Telegram API ID and Hash (from my.telegram.org)

---

### 3️⃣ Configuration

Create a `config.py` file:

```python
API_ID = 12345678
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

DATABASE_URI = "mongodb://localhost:27017"
DATABASE_NAME = "file_sharing_bot"

DB_CHANNEL = -1001234567890
FORCE_SUB_CHANNELS = []

OWNER_ID = 123456789
ADMINS = [123456789]

PORT = 8080
WEBHOOK = False
```

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Awakener_Bots/File-Store
cd File-Store
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configuration

Fill a `setup.json` file:

```python
[
    {
        "session": "ses1",
        "token": "BOT_TOKEN",
        "api_id": "12345678",
        "api_hash": "",
        "workers": 8,
        "db_uri": "mongodb+srv://Awakeners-bots-Powered-by",
        "db_name": "Awakenersbots",
        "fsubs": [],
        "db": -1234567890,
        "auto_del": 300,
        "messages": {
            "START": "<b><blockquote><b><blockquote>Moshi Moshi Senpai {mention}</blockquote></b>\n<b>I'm Akuma Sama a Filestore bot of @Anime_Mortals</b></blockquote>",
            "FSUB": "Hᴇʟʟᴏ Sᴇɴᴘᴀɪ {mention}\n\n<b>Yᴏᴜ Nᴇᴇᴅ Tᴏ Jᴏɪɴ Iɴ Mʏ Cʜᴀɴɴᴇʟs Tᴏ Gᴇᴛ Fɪʟᴇs</b>",
            "ABOUT": "<b><blockquote expandable>╭───────────────⍟\n├➽ Dᴇᴠᴇʟᴏᴩᴇʀ : <a href=\"https://t.me/GPGMS0\"><b>GPG</b></a>\n├➽ Oᴡɴᴇʀ : <a href=\"https://t.me/GPGMS0\"><b>𝗚𝗣𝗚</b></a>\n├➽ Aɴɪᴍᴇ Iɴᴅᴇx : <a href=\"https://t.me/Anime_Mortals\"><b>Aɴɪᴍᴇ Mᴏʀᴛᴀʟs</b></a>\n├➽ Fɪɴɪsʜᴇᴅ Aɴɪᴍᴇ : <a href=\"https://t.me/Anime_Awakeners\"><b>Aɴɪᴍᴇ Aᴡᴀᴋᴇɴᴇʀs</b></a>\n├➽ Oɴɢᴏɪɴɢ Aɴɪᴍᴇ : <a href=\"https://t.me/Ongoing_Mortals\"><b>Oɴɢᴏɪɴɢ Mᴏʀᴛᴀʟ</b></a>\n├➽ Mᴀɴʜᴡᴀ / Mᴀɴɢᴀ : <a href=\"https://t.me/Manhwa_Mortals\"><b>Mᴀɴʜᴡᴀ Mᴏʀᴛᴀʟs</b></a>\n├➽ Nᴇᴛᴡᴏʀᴋ : <a href=\"https://t.me/The_Awakeners\"><b>Tʜᴇ Aᴡᴀᴋᴇɴᴇʀs</b></a>\n├➽ Rᴇǫ/Cʜᴀᴛ : <a href=\"https://t.me/Mortals_Realm\"><b>Mᴏʀᴛᴀʟs Rᴇᴀʟᴍ</b></a>\n╰───────────────⍟</blockquote></b>",
            "REPLY": "<b><blockquote>❌𝗗𝗼𝗻'𝘁 𝘀𝗲𝗻𝗱 𝗺𝗲 𝗱𝗶𝗿𝗲𝗰𝘁 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗶𝗻 𝗱𝗺, 𝗱𝗼 𝘆𝗼𝘂 𝗵𝗮𝘃𝗲 𝗮 𝗱𝗲𝗮𝘁𝗵 𝘄𝗶𝘀𝗵?</blockquote></b>",
            "START_PHOTO": "",
            "FSUB_PHOTO": ""
        },
        "admins": [
            123456789,
            987654321
        ],
        "disable_btn": true,
        "protect": false,
        "credit_config": {
            "expiry_days": 30,
            "referral_reward": 5,
            "payment_method": "manual",
            "upi_id": "GPGpapaji@Fam",
            "phone": "XXXXXXXXXX",
            "packages": [
                {
                    "id": "pkg_10",
                    "credits": 10,
                    "price": 50,
                    "currency": "INR"
                },
                {
                    "id": "pkg_25",
                    "credits": 25,
                    "price": 100,
                    "currency": "INR",
                    "popular": true
                },
                {
                    "id": "pkg_50",
                    "credits": 50,
                    "price": 180,
                    "currency": "INR"
                },
                {
                    "id": "pkg_100",
                    "credits": 100,
                    "price": 300,
                    "currency": "INR"
                }
            ]
        },
        "token_config": {
            "token_expiry_minutes": 10,
            "max_bypass_attempts": 5,
            "bypass_check_hours": 24
        },
        "auto_batch_config": {
            "enabled": true,
            "time_window_seconds": 30,
            "min_files_for_batch": 2
        }
    }
]
```

### 4️⃣ Run the Bot

```bash
python main.py
```

---

## 📝 Commands
# Telegram Bot – Command Reference

This document lists all available commands for the bot, based on the provided source code.

---

## 👤 User Commands  
*(Available to everyone)*

| Command | Description |
|--------|-------------|
| `/start` | (Likely present) Starts the bot and shows the welcome message. |
| `/credits` | Check your credit balance, expiry date, and referral statistics. |
| `/referral` | Get your unique referral link and view earnings from referrals. |
| `/buycredits` | Display available credit packages and start the purchase process. |
| `/premium` | Show premium membership plans and their benefits. |
| `/mypremium` | Check your own premium status and expiry date. |
| `/checkpremium [user_id]` | Check premium status – for yourself (no argument) or for another user (if you are an admin). |
| `/usage` | View system resource usage (CPU, RAM, disk, network). |

---

## 🔧 Admin Commands  
*(Require the user to be in the bot’s admin list or be the owner)*

### 💳 Credit System
| Command | Description |
|--------|-------------|
| `/addcredit <user_id> <amount> [expiry_days]` | Add credits to a user with optional expiry. |
| `/setcredit <user_id> <amount> [expiry_days]` | Set the exact credit amount for a user. |
| `/removecredit <user_id>` | Remove all credits from a user. |
| `/listcredits` | List all users who have credits (first 20). |
| `/creditstats` | Show overall credit system statistics. |
| `/approvepayment <payment_id>` | Manually approve a payment and credit the user. |

### 🤖 Batch & Link Generation
| Command | Description |
|--------|-------------|
| `/autobatch` | Start the manual batch creation process (send message links). |
| `/cancelbatch` | Cancel an ongoing batch creation. |
| `/batch` | Create a batch link from a range of messages (forward or links). |
| `/genlink` | Generate a single file link from a forwarded message or post. |

### 🚫 User Management
| Command | Description |
|--------|-------------|
| `/ban <user_id> [user_id2 ...]` | Ban one or more users. |
| `/unban <user_id> [user_id2 ...]` | Unban one or more users. |

### 💎 Premium Management
| Command | Description |
|--------|-------------|
| `/addpremium <user_id> [days]` | Grant premium to a user (use 0 days for lifetime). |
| `/removepremium <user_id>` | Remove premium from a user. |
| `/premiumusers` | List all premium users with remaining days. |

### 🔁 Auto‑Forward (Owner Only)
| Command | Description |
|--------|-------------|
| `/set_forward_config <source_id> <dest_id>` | Set source and destination channels for auto‑forwarding. |
| `/forward_old <start_msg_id> <end_msg_id>` | Manually forward a range of old messages. |

---

**Notes:**

- Some commands (especially admin ones) use interactive prompts – the bot will ask for additional input after the command.
- The bot supports multiple instances via `setup.json`; commands apply to the specific bot you are talking to.
- Settings like auto‑batch are configured through callback buttons in the admin panel, not by commands.
- 

---

## 🗂️ Project Structure

```
file-sharing-bot/
├── bot.py
├── config.py
├── requirements.txt
├── plugins/
├── helper/
└── README.md
```

---

## 👨‍💻 ᴄʀᴇᴅɪᴛs

**ᴅᴇᴠᴇʟᴏᴘᴇʀ**

» [ɢᴘɢ](https://github.com/GPG36)

» [ᴋᴜɴᴀʟ](https://github.com/KunalG932)

**ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ**  
» [ᴀᴡᴀᴋᴇɴᴇʀs ʙᴏᴛs](https://t.me/Awakeners_Bots)

» [ᴠᴏᴀᴛ](t.me/Awakeners_bots) - [ʙᴀsᴇ ʀᴇᴘᴏ](https://github.com/ArihantSharma/FileStoreBot)
## ⚠️ Disclaimer

This bot is for educational purposes. Ensure compliance with Telegram's Terms of Service and local laws.

---
<p align="center">
  ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ <a href="https://t.me/Awakeners_Bots">ᴀᴡᴀᴋᴇɴᴇʀs ʙᴏᴛs</a>
</p>

<p align="center">
⭐ Star this repository if you find it helpful!
</p>
