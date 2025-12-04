# cogs/tickets.py

import io
import time
import asyncio

import discord
from discord.ext import commands
from discord import app_commands

from config import ADMIN_ROLE_IDS, LOG_CHANNEL_ID


def is_staff(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    return any(r.id in ADMIN_ROLE_IDS for r in member.roles)


async def close_ticket_with_transcript(channel: discord.TextChannel):
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        ts = msg.created_at.isoformat()
        author = f"{msg.author} ({msg.author.id})"
        content = msg.content.replace("\n", "\\n")
        messages.append(f"[{ts}] {author}: {content}")

    transcript_text = "\n".join(messages) or "No messages."

    fp = io.BytesIO(transcript_text.encode("utf-8"))
    fp.name = f"ticket_{channel.id}_transcript.txt"

    guild = channel.guild
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if isinstance(log_channel, discord.TextChannel):
        await log_channel.send(
            content=f"📁 Ticket transcript from {channel.mention}",
            file=discord.File(fp),
        )

    await channel.send("✅ Transcript saved. Deleting channel in 5 seconds...")
    await asyncio.sleep(5)
    await channel.delete(reason="Ticket closed")


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if not isinstance(interaction.user, discord.Member):
            return

        if not is_staff(interaction.user):
            await interaction.response.send_message(
                "❌ Only staff can close tickets.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        await interaction.channel.send(  # type: ignore
            "🛑 Ticket closing, generating transcript..."
        )
        await close_ticket_with_transcript(interaction.channel)  # type: ignore


class TicketsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_ticket_category(self, guild: discord.Guild):
        for cat in guild.categories:
            if cat.name.lower() == "tickets":
                return cat
        return await guild.create_category("Tickets")

    @app_commands.command(
        name="ticket",
        description="Open a support ticket.",
    )
    @app_commands.describe(
        reason="Short description of your problem.",
    )
    async def ticket(
        self,
        interaction: discord.Interaction,
        reason: str,
    ):
        guild = interaction.guild
        user = interaction.user
        if not isinstance(guild, discord.Guild) or not isinstance(
            user, discord.Member
        ):
            await interaction.response.send_message(
                "❌ Ticket can only be used in a server.",
                ephemeral=True,
            )
            return

        category = await self.ensure_ticket_category(guild)
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            topic=f"Ticket by {user} | Reason: {reason}",
        )

        await channel.set_permissions(user, read_messages=True, send_messages=True)
        await channel.set_permissions(
            guild.default_role,
            read_messages=False,
            send_messages=False,
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True,
        )

        embed = discord.Embed(
            title="🎫 New Ticket",
            description=f"Opened by {user.mention}\nReason: `{reason}`",
            color=discord.Color.green(),
        )
        view = TicketView()
        await channel.send(content=user.mention, embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketsCog(bot))
