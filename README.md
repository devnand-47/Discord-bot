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

## 🛠️ Installation

### 1. Prerequisites
* Python 3.9 or higher
* A Discord Bot Token (from the [Discord Developer Portal](https://discord.com/developers/applications))
* (Optional) OpenAI API Key

### 2. Clone the Repository
```bash
git clone https://github.com/devnand-47/Discord-bot
cd UltimateBot
