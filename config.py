# ========= BOT TOKEN =========
TOKEN = "YOUT_BOT_TOKEN HERE"

# ========= IDs =========
GUILD_ID = 123131231231312313  # main server

# Channels
RULES_CHANNEL_ID = 123123213123123         # #rules
WELCOME_CHANNEL_ID = 130846133123123123904946593       # #welcome
DEFAULT_ANNOUNCE_CHANNEL_ID = 12312312312312313  # #announcements
LOG_CHANNEL_ID = 123213123123           # dedicated #logs channel

# Roles considered staff/admin
ADMIN_ROLE_IDS = [
    1231231313123123,  # @Admin
]

# ========= STORAGE =========
DB_PATH = "data/ultimatebot.db"
BACKUP_ROOT = "data/backups"
BACKUP_MESSAGES_PER_CHANNEL = 200

# ========= DASHBOARD AUTH =========
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "DEV"  # change to stronger password
DASHBOARD_SECRET_KEY = "super-secret-key-change-this"

# ========= AUTO-MOD / RAID PROTECTION =========
VERIFICATION_CHANNEL_ID = 12344556778  # #verification
VERIFIED_ROLE_ID = 123435345345        # @Verified

RAID_JOIN_WINDOW = 30
RAID_JOIN_THRESHOLD = 5
LOCKDOWN_HARD_THRESHOLD = 15

FIREWALL_AUTO_RELEASE_MINUTES = -1  # set to -1 to disable auto-release
CAPTCHA_EXPIRE_SECONDS = 300
