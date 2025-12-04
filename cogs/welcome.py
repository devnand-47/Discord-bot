# cogs/welcome.py

import discord
from discord.ext import commands
from discord import app_commands

from config import (
    GUILD_ID,
    RULES_CHANNEL_ID,
    WELCOME_CHANNEL_ID,
    ADMIN_ROLE_IDS,
    VERIFICATION_CHANNEL_ID,   # NEW
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
            "❌ Admin only.", ephemeral=True
        )
        raise app_commands.CheckFailure("Not admin")

    return app_commands.check(predicate)


class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------- DB helpers ----------

    async def get_settings(self, guild_id: int):
        assert self.bot.db is not None
        cur = await self.bot.db.execute(
            """
            SELECT welcome_channel_id, welcome_message, autorole_id, default_announce_id
            FROM guild_settings WHERE guild_id = ?
            """,
            (guild_id,),
        )
        row = await cur.fetchone()
        if row is None:
            return None
        return {
            "welcome_channel_id": row[0],
            "welcome_message": row[1],
            "autorole_id": row[2],
            "default_announce_id": row[3],
        }

    async def upsert_settings(
        self,
        guild_id: int,
        welcome_channel_id: int | None = None,
        welcome_message: str | None = None,
        autorole_id: int | None = None,
        default_announce_id: int | None = None,
    ):
        assert self.bot.db is not None
        current = await self.get_settings(guild_id) or {
            "welcome_channel_id": None,
            "welcome_message": None,
            "autorole_id": None,
            "default_announce_id": None,
        }

        if welcome_channel_id is not None:
            current["welcome_channel_id"] = welcome_channel_id
        if welcome_message is not None:
            current["welcome_message"] = welcome_message
        if autorole_id is not None:
            current["autorole_id"] = autorole_id
        if default_announce_id is not None:
            current["default_announce_id"] = default_announce_id

        await self.bot.db.execute(
            """
            INSERT INTO guild_settings (guild_id, welcome_channel_id, welcome_message, autorole_id, default_announce_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
              welcome_channel_id = excluded.welcome_channel_id,
              welcome_message    = excluded.welcome_message,
              autorole_id        = excluded.autorole_id,
              default_announce_id= excluded.default_announce_id
            """,
            (
                guild_id,
                current["welcome_channel_id"],
                current["welcome_message"],
                current["autorole_id"],
                current["default_announce_id"],
            ),
        )
        await self.bot.db.commit()

    # ---------- event: on_member_join ----------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        settings = await self.get_settings(guild.id) or {}

        rules_channel = guild.get_channel(RULES_CHANNEL_ID) if RULES_CHANNEL_ID else None
        verification_channel = (
            guild.get_channel(VERIFICATION_CHANNEL_ID)
            if VERIFICATION_CHANNEL_ID
            else None
        )

        welcome_channel_id = settings.get("welcome_channel_id") or WELCOME_CHANNEL_ID
        welcome_channel = (
            guild.get_channel(welcome_channel_id) if welcome_channel_id else None
        )

        welcome_message = settings.get("welcome_message") or (
            "{mention}, welcome to **{server}**.\n"
            "You are now entering a monitored cyber operations zone."
        )

        description = welcome_message.format(
            mention=member.mention,
            server=guild.name,
        )

        embed = discord.Embed(
            title="🚨 New Operative Connected",
            description=description,
            color=discord.Color.red(),
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        elif guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if rules_channel:
            embed.add_field(
                name="📜 Briefing",
                value=f"Read {rules_channel.mention} before starting any operation.",
                inline=False,
            )

        if verification_channel:
            embed.add_field(
                name="🧩 Verification",
                value=f"Complete verification in {verification_channel.mention} to unlock the server.",
                inline=False,
            )

        # ----- DM to user (with button that jumps to #verification) -----
        dm_view = None
        if verification_channel:
            dm_view = discord.ui.View()
            url = f"https://discord.com/channels/{guild.id}/{verification_channel.id}"
            dm_view.add_item(
                discord.ui.Button(
                    label="Go to Verification Channel",
                    url=url,
                    style=discord.ButtonStyle.link,
                )
            )

        try:
            await member.send(
                content=f"Welcome to **{guild.name}**, {member.display_name}. 🛰",
                embed=embed,
                view=dm_view,
            )
        except discord.Forbidden:
            pass

        # ----- Message in welcome channel -----
        if welcome_channel:
            await welcome_channel.send(content=member.mention, embed=embed)

        # Autorole
        autorole_id = settings.get("autorole_id")
        if autorole_id:
            role = guild.get_role(autorole_id)
            if role:
                try:
                    await member.add_roles(role, reason="Auto role on join")
                except discord.Forbidden:
                    pass

    # ---------- /welcome_set_channel ----------

    @app_commands.command(
        name="welcome_set_channel",
        description="Set the welcome channel.",
    )
    @is_admin()
    async def welcome_set_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ):
        await self.upsert_settings(
            interaction.guild.id, welcome_channel_id=channel.id  # type: ignore
        )
        await interaction.response.send_message(
            f"✅ Welcome channel set to {channel.mention}.",
            ephemeral=True,
        )

    # ---------- /welcome_set_message ----------

    @app_commands.command(
        name="welcome_set_message",
        description="Set the welcome message template.",
    )
    @is_admin()
    @app_commands.describe(
        template="Use {mention} and {server} placeholders.",
    )
    async def welcome_set_message(
        self,
        interaction: discord.Interaction,
        template: str,
    ):
        await self.upsert_settings(
            interaction.guild.id, welcome_message=template  # type: ignore
        )
        await interaction.response.send_message(
            "✅ Welcome message updated.",
            ephemeral=True,
        )

    # ---------- /welcome_set_autorole ----------

    @app_commands.command(
        name="welcome_set_autorole",
        description="Set an autorole for new members.",
    )
    @is_admin()
    async def welcome_set_autorole(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        await self.upsert_settings(
            interaction.guild.id, autorole_id=role.id  # type: ignore
        )
        await interaction.response.send_message(
            f"✅ Autorole set to {role.mention}.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))
