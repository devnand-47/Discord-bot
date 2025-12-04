# bot.py

import os
from typing import Optional

import discord
from discord.ext import commands
import aiosqlite

from config import TOKEN, GUILD_ID, DB_PATH

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class UltimateBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )
        self.db: Optional[aiosqlite.Connection] = None

    async def setup_hook(self) -> None:
        # Ensure data dir
        os.makedirs("data", exist_ok=True)

        # Database
        self.db = await aiosqlite.connect(DB_PATH)
        await self._init_db()

        # Load cogs
        for ext in (
            "cogs.admin",
            "cogs.welcome",
            "cogs.backups",
            "cogs.tickets",
            "cogs.fun",
            "cogs.automod",      # NEW
            "cogs.moderation",   # NEW
            "cogs.roles",        # NEW
            "cogs.ai",           # NEW
            "cogs.help",         # NEW
        ):
            await self.load_extension(ext)

        # Sync slash commands
        try:
            if GUILD_ID:
                guild_obj = discord.Object(id=GUILD_ID)
                self.tree.copy_global_to(guild=guild_obj)
                await self.tree.sync(guild=guild_obj)
                print(f"[SYNC] Slash commands synced to guild {GUILD_ID}")
            else:
                await self.tree.sync()
                print("[SYNC] Slash commands synced globally")
        except discord.Forbidden as e:
            print(f"[SYNC] Forbidden when syncing to guild {GUILD_ID}: {e}")
            print("[SYNC] Falling back to global sync...")
            await self.tree.sync()

    async def _init_db(self):
        assert self.db is not None
        await self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id            INTEGER PRIMARY KEY,
                welcome_channel_id  INTEGER,
                welcome_message     TEXT,
                autorole_id         INTEGER,
                default_announce_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS scheduled_announcements (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                channel_id  INTEGER,
                message     TEXT,
                run_at      INTEGER,
                sent        INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS moderation_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                user_id     INTEGER,
                actor_id    INTEGER,
                action      TEXT,
                reason      TEXT,
                created_at  INTEGER
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id        INTEGER,
                channel_id      INTEGER,
                opener_id       INTEGER,
                status          TEXT,
                created_at      INTEGER,
                closed_at       INTEGER
            );
            """
        )
        await self.db.commit()


bot = UltimateBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Guilds I am in:")
    for g in bot.guilds:
        print(f"- {g.name} ({g.id})")


if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("ERROR: Set TOKEN in config.py")
    bot.run(TOKEN)
