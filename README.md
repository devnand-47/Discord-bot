# UltimateBot – Advanced Discord Operations Assistant

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Discord.py](https://img.shields.io/badge/Discord.py-2.0%2B-5865F2?style=for-the-badge&logo=discord)
![FastAPI](https://img.shields.io/badge/FastAPI-Dashboard-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**UltimateBot** is a modular, cybersecurity-themed Discord bot designed for server administration, automated defense, and analytics. It features a **FastAPI web dashboard**, **SQLite logging**, **Anti-Raid Firewall**, and **OpenAI integration**.

---

## ⚡ Key Features

### 🛡️ Security & Auto-Moderation
* **Raid Firewall & CAPTCHA:** Automatically locks down the server during join spikes and challenges new users with a web-style CAPTCHA button interaction before allowing access.
* **Automated Filters:** Real-time scanning for spam, bad words, and unauthorized invite links.
* **Lockdown Mode:** Instantly lock specific channels or the entire server during emergencies.
* **Logging:** Comprehensive database logging of all moderation actions (Kicks, Bans, Timeouts, Auto-mod triggers).

### 📊 Web Dashboard
Includes a built-in **FastAPI** web interface to visualize server data:
* **Interactive Graphs:** View moderation activity trends over time.
* **Live Logs:** Read the last 20 moderation actions directly from the browser.
* **Settings Management:** Configure welcome messages, auto-roles, and announcement channels via the web UI.
* **Secure Auth:** Cookie-based session login system.

### ⚙️ Administration & Utilities
* **Scheduled Announcements:** Queue announcements to be sent at specific times across the network.
* **Channel Backups:** Create local text-file backups of channel history for archival purposes.
* **Ticket System:** Slash command support for private support tickets.
* **Role Menus:** Self-assignable roles via buttons.

### 🤖 AI Core
* **OpenAI Integration:** Chat with the bot using `/ai` or `!core` for intelligent, cyber-themed responses.

---
```
## 🛠️ Installation

### 1. Prerequisites
* Python 3.9 or higher
* A Discord Bot Token (from the [Discord Developer Portal](https://discord.com/developers/applications))
* (Optional) OpenAI API Key

### 2. Clone the Repository
```bash
git clone https://github.com/devnand-47/Discord-bot
cd UltimateBot
```
```
3. Install DependenciesCreate a virtual environment (recommended) and install the required packages:Bash# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
Note: Create a requirements.txt with the following content if it doesn't exist:Plaintextdiscord.py
aiosqlite
fastapi
uvicorn
python-multipart
openai
itsdangerous

4. ConfigurationOpen config.py and configure your settings.⚠️ IMPORTANT: Never commit your actual Token or API keys to GitHub. Use environment variables or a .env file in production.Python# config.py

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
GUILD_ID = 123456789012345678  # Your Main Server ID

```# Dashboard Credentials (CHANGE THESE!)
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "CHANGE_ME"
DASHBOARD_SECRET_KEY = "complex-random-string"
```

# IDs for roles and channels
LOG_CHANNEL_ID = 123...
VERIFICATION_CHANNEL_ID = 123...
🚀 UsageRunning the BotTo start the Discord bot (and the database):Bashpython bot.py
Running the DashboardTo start the web dashboard (runs separately or in parallel):Bashuvicorn dashboard:app --reload --port 8000
Access the dashboard at: localhost 📖 Command ReferenceAdmin (Slash Commands)CommandDescription/firewall <mode>Turn Anti-Raid Firewall on, off, or view status./announce <msg>Send a styled embed announcement./schedule_announceSchedule a message to be sent later./backup_nowForce a text backup of guild channels./lockdown <bool>Lock or unlock a channel./logs <limit>View recent moderation logs.ModerationCommandDescription/kick <user>Kick a member./ban <user>Ban a member./mute <user> <time>Timeout a member./clear <amount>Bulk delete messages.GeneralCommandDescription/ai <message>Ask the AI assistant a question./ticketOpen a support ticket.!pingCheck bot latency.

📂 Project StructureUltimateBot/
```
├── bot.py               # Main bot entry point
├── config.py            # Configuration variables
├── dashboard.py         # FastAPI web dashboard
├── requirements.txt     # Python dependencies
├── data/                # Database and Backups (Auto-generated)
└── cogs/
    ├── admin.py         # Admin commands
    ├── automod.py       # Firewall and Anti-Spam
    ├── moderation.py    # Kick/Ban/Mute
    ├── ai.py            # OpenAI Integration
    ├── backups.py       # Channel backup logic
    ├── help.py          # Custom help menu
    └── ...
```
