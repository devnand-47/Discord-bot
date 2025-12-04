# cogs/admin.py

import time
from typing import Optional

import discord
from discord.ext import commands, tasks
from discord import app_commands

from config import (
    ADMIN_ROLE_IDS,
    LOG_CHANNEL_ID,
)


def is_admin():
    async def predicate(interaction: discord.Interaction):
        member = interaction.user
        if isinstance(member, discord.Member):
            if member.guild_permissions.administrator:
                return True
            if any(r.id in ADMIN_ROLE_IDS for r in member.roles):
                return True

        await interaction.response.send_message(
            "❌ You must be an administrator / staff to use this command.",
            ephemeral=True,
        )
        raise app_commands.CheckFailure("Not admin")

    return app_commands.check(predicate)


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_scheduled_announcements.start()

    def cog_unload(self):
        self.check_scheduled_announcements.cancel()

    # ---------- internal: moderation log ----------

    async def log_action(
        self,
        guild: discord.Guild,
        actor: discord.abc.User,
        user: Optional[discord.abc.User],
        action: str,
        reason: str = "",
    ):
        if self.bot.db is None:
            return

        user_id = user.id if user else 0
        actor_id = actor.id
        now = int(time.time())

        await self.bot.db.execute(
            """
            INSERT INTO moderation_logs (guild_id, user_id, actor_id, action, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (guild.id, user_id, actor_id, action, reason, now),
        )
        await self.bot.db.commit()

        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if isinstance(log_channel, discord.TextChannel):
            embed = discord.Embed(
                title="🔍 Moderation Log",
                description=f"**Action:** {action}",
                color=discord.Color.orange(),
            )
            if user:
                embed.add_field(
                    name="Target", value=f"{user} ({user.id})", inline=False
                )
            embed.add_field(
                name="Actor", value=f"{actor} ({actor.id})", inline=False
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=embed)

    # ---------- /announce ----------

    @app_commands.command(
        name="announce",
        description="Send a cyber-style announcement.",
    )
    @is_admin()
    @app_commands.describe(
        message="Text of the announcement.",
        channel="Channel to send in (optional).",
    )
    async def announce(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: Optional[discord.TextChannel] = None,
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Guild not found.", ephemeral=True
            )
            return

        if channel is None:
            # if you want, you can read default channel from DB here
            channel = interaction.channel  # type: ignore

        if channel is None:
            await interaction.response.send_message(
                "❌ I couldn't find a channel to send the announcement.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="⚠ Network-Wide Broadcast",
            description=message,
            color=discord.Color.from_rgb(0, 255, 255),
        )
        embed.set_footer(text=f"Transmission by {interaction.user.display_name}")

        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Announcement sent in {channel.mention}.",
            ephemeral=True,
        )

        await self.log_action(
            guild=guild,
            actor=interaction.user,
            user=None,
            action="announce",
            reason=f"Channel: #{channel.name}",
        )

    # ---------- scheduled announcements ----------

    @app_commands.command(
        name="schedule_announce",
        description="Schedule an announcement for later.",
    )
    @is_admin()
    @app_commands.describe(
        message="Text of the announcement.",
        delay_minutes="Delay before sending (in minutes).",
        channel="Channel to send in (optional).",
    )
    async def schedule_announce(
        self,
        interaction: discord.Interaction,
        message: str,
        delay_minutes: app_commands.Range[int, 1, 60 * 24],
        channel: Optional[discord.TextChannel] = None,
    ):
        guild = interaction.guild
        if guild is None or self.bot.db is None:
            await interaction.response.send_message(
                "❌ Scheduling failed (no guild/db).", ephemeral=True
            )
            return

        if channel is None:
            channel = interaction.channel  # type: ignore

        if channel is None:
            await interaction.response.send_message(
                "❌ I couldn't find a channel to schedule in.",
                ephemeral=True,
            )
            return

        run_at = int(time.time()) + delay_minutes * 60

        await self.bot.db.execute(
            """
            INSERT INTO scheduled_announcements (guild_id, channel_id, message, run_at)
            VALUES (?, ?, ?, ?)
            """,
            (guild.id, channel.id, message, run_at),
        )
        await self.bot.db.commit()

        await interaction.response.send_message(
            f"✅ Scheduled announcement in {channel.mention} in {delay_minutes} minute(s).",
            ephemeral=True,
        )

        await self.log_action(
            guild=guild,
            actor=interaction.user,
            user=None,
            action="schedule_announce",
            reason=f"Channel: #{channel.name}, delay={delay_minutes}m",
        )

    @tasks.loop(seconds=60)
    async def check_scheduled_announcements(self):
        if self.bot.db is None:
            return

        now = int(time.time())
        cursor = await self.bot.db.execute(
            """
            SELECT id, guild_id, channel_id, message
            FROM scheduled_announcements
            WHERE sent = 0 AND run_at <= ?
            """,
            (now,),
        )
        rows = await cursor.fetchall()

        for ann_id, guild_id, channel_id, message in rows:
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                continue
            channel = guild.get_channel(channel_id)
            if not isinstance(channel, discord.TextChannel):
                continue

            embed = discord.Embed(
                title="📡 Scheduled Transmission",
                description=message,
                color=discord.Color.blue(),
            )
            await channel.send(embed=embed)

            await self.bot.db.execute(
                "UPDATE scheduled_announcements SET sent = 1 WHERE id = ?",
                (ann_id,),
            )
        await self.bot.db.commit()

    @check_scheduled_announcements.before_loop
    async def before_check_scheduled_announcements(self):
        await self.bot.wait_until_ready()

    # ---------- /clear ----------

    @app_commands.command(
        name="clear",
        description="Clear messages in a channel (admin only).",
    )
    @is_admin()
    @app_commands.describe(
        amount="How many messages to delete (1–200).",
        channel="Channel to clear (default: current).",
    )
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 200],
        channel: Optional[discord.TextChannel] = None,
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Guild not found.", ephemeral=True
            )
            return

        target_channel = channel or interaction.channel  # type: ignore
        deleted = await target_channel.purge(limit=amount + 1)
        count = max(len(deleted) - 1, 0)

        await interaction.response.send_message(
            f"🧹 Cleared `{count}` messages in {target_channel.mention}.",
            ephemeral=True,
        )

        await self.log_action(
            guild=guild,
            actor=interaction.user,
            user=None,
            action="clear",
            reason=f"{count} messages in #{target_channel.name}",
        )

    # ---------- /slowmode ----------

    @app_commands.command(
        name="slowmode",
        description="Set slowmode on a channel (admin only).",
    )
    @is_admin()
    @app_commands.describe(
        seconds="Slowmode delay in seconds (0 to disable).",
        channel="Channel to apply to (default: current).",
    )
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: app_commands.Range[int, 0, 21600],
        channel: Optional[discord.TextChannel] = None,
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Guild not found.", ephemeral=True
            )
            return

        target_channel = channel or interaction.channel  # type: ignore
        await target_channel.edit(slowmode_delay=seconds)

        msg = (
            f"🐢 Enabled slowmode `{seconds}`s in {target_channel.mention}."
            if seconds > 0
            else f"🚀 Disabled slowmode in {target_channel.mention}."
        )

        await interaction.response.send_message(msg, ephemeral=True)

        await self.log_action(
            guild=guild,
            actor=interaction.user,
            user=None,
            action="slowmode",
            reason=f"{seconds}s in #{target_channel.name}",
        )

    # ---------- /lockdown ----------

    @app_commands.command(
        name="lockdown",
        description="Lock or unlock a channel (admin only).",
    )
    @is_admin()
    @app_commands.describe(
        locked="True = lock channel, False = unlock.",
        channel="Channel to lock/unlock (default: current).",
    )
    async def lockdown(
        self,
        interaction: discord.Interaction,
        locked: bool,
        channel: Optional[discord.TextChannel] = None,
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Guild not found.", ephemeral=True
            )
            return

        target_channel = channel or interaction.channel  # type: ignore
        overwrite = target_channel.overwrites_for(guild.default_role)
        overwrite.send_messages = None if not locked else False
        await target_channel.set_permissions(guild.default_role, overwrite=overwrite)

        status = "🔒 Channel locked." if locked else "🔓 Channel unlocked."
        await interaction.response.send_message(
            f"{status} {target_channel.mention}", ephemeral=True
        )

        await self.log_action(
            guild=guild,
            actor=interaction.user,
            user=None,
            action="lockdown",
            reason=f"{'locked' if locked else 'unlocked'} #{target_channel.name}",
        )

    # ---------- /logs ----------

    @app_commands.command(
        name="logs",
        description="View last moderation logs.",
    )
    @is_admin()
    @app_commands.describe(
        limit="How many entries to show (1–50).",
    )
    async def logs(
        self,
        interaction: discord.Interaction,
        limit: app_commands.Range[int, 1, 50] = 10,
    ):
        guild = interaction.guild
        if guild is None or self.bot.db is None:
            await interaction.response.send_message(
                "❌ Cannot fetch logs.", ephemeral=True
            )
            return

        cur = await self.bot.db.execute(
            """
            SELECT user_id, actor_id, action, reason, created_at
            FROM moderation_logs
            WHERE guild_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (guild.id, limit),
        )
        rows = await cur.fetchall()

        if not rows:
            await interaction.response.send_message(
                "ℹ No moderation logs yet.", ephemeral=True
            )
            return

        lines = []
        for user_id, actor_id, action, reason, created_at in rows:
            ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(created_at))
            user_txt = f"{user_id}" if user_id else "-"
            reason_txt = reason or "-"
            lines.append(
                f"[{ts}] action={action}, target={user_txt}, by={actor_id}, reason={reason_txt}"
            )

        text = "```" + "\n".join(lines) + "```"
        await interaction.response.send_message(text, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
