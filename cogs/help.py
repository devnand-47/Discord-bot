# cogs/help.py

import discord
from discord.ext import commands
from discord import app_commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --------- internal helper to build a single help embed ---------

    def build_main_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="UltimateBot – Command Reference",
            description=(
                "Cyber operations assistant for your server.\n"
                "Use `/` for admin slash commands and `!` for fun/user commands."
            ),
            color=discord.Color.teal(),
        )

        # Admin / Moderation
        embed.add_field(
            name="🛡️ Admin & Moderation (Slash)",
            value=(
                "**/announce** `<message> [channel]` – Broadcast announcement\n"
                "**/schedule_announce** – Schedule an announcement\n"
                "**/clear** `<amount>` – Clear messages\n"
                "**/slowmode** `<seconds>` – Set channel slowmode\n"
                "**/lockdown** – Lock channel\n"
                "**/backup_now** – Run channel/message backup\n"
                "**/kick** `<user> [reason]` – Kick member\n"
                "**/ban** `<user> [reason]` – Ban member\n"
                "**/mute** `<user> <minutes> [reason]` – Timeout user\n"
                "**/unmute** `<user>` – Remove timeout\n"
                "**/logs** `[limit]` – View moderation logs"
            ),
            inline=False,
        )

        # Welcome / Config
        embed.add_field(
            name="📥 Welcome & Config (Slash)",
            value=(
                "**/welcome_set_channel** `<#channel>` – Set welcome channel\n"
                "**/welcome_set_message** `<template>` – Set welcome text\n"
                "**/welcome_set_autorole** `<@role>` – Set auto-role for new members"
            ),
            inline=False,
        )

        # Tickets
        embed.add_field(
            name="🎫 Tickets (Slash)",
            value=(
                "**/ticket** – Open a support ticket channel\n"
                "Use the close button in the ticket to end it; transcript is saved."
            ),
            inline=False,
        )

        # Roles / Reaction roles
        embed.add_field(
            name="🎛️ Roles & Menus (Slash)",
            value=(
                "**/rolemenu** `<role1> [role2] [role3]` – Create a button role menu "
                "so users can click to get/remove roles."
            ),
            inline=False,
        )

        # AI / Fun
        embed.add_field(
            name="🤖 AI & Fun (Prefix `!` + Slash)",
            value=(
                "**/ai** `<message>` – Ask the AI core (short cyber replies)\n"
                "**!core** `<message>` – Same AI core via prefix\n"
                "**!ping** – Bot latency\n"
                "**!meme** – Random meme\n"
                "**!8ball** `<question>` – Magic 8-ball\n"
                "**!chat** `<message>` – Simple fun chat reply"
            ),
            inline=False,
        )

        # Automod / Info
        embed.add_field(
            name="🧱 Auto-Moderation (Automatic)",
            value=(
                "Bad-word filter, anti-spam, anti-invite and raid detection run automatically.\n"
                "Events are logged to the moderation database and appear on the dashboard graph."
            ),
            inline=False,
        )

        embed.set_footer(text="Use /help or !help any time to see this menu again.")
        return embed

    # --------- Slash help ---------

    @app_commands.command(
        name="help",
        description="Show all UltimateBot commands and categories.",
    )
    async def help_slash(self, interaction: discord.Interaction):
        embed = self.build_main_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --------- Prefix help ---------

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context):
        embed = self.build_main_embed()
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
