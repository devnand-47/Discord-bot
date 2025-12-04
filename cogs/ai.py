# cogs/ai.py

import os

import discord
from discord.ext import commands
from discord import app_commands

try:
    import openai
except ImportError:
    openai = None


class AICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and openai:
            openai.api_key = self.api_key

    def simple_reply(self, text: str) -> str:
        text = text.lower()
        if "hello" in text or "hi" in text:
            return "Hello. Monitoring channel.…"
        if "help" in text:
            return "Describe the issue and I will route it mentally to the admin."
        return "Noted. Adding to threat database."

    async def ai_answer(self, prompt: str) -> str:
        if not (self.api_key and openai):
            return self.simple_reply(prompt)

        try:
            resp = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a short, cyber-security themed Discord assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
            )
            return resp.choices[0].message["content"].strip()
        except Exception:
            return self.simple_reply(prompt)

    @app_commands.command(
        name="ai",
        description="Chat with the AI core.",
    )
    async def ai_slash(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(thinking=True)
        reply = await self.ai_answer(message)
        await interaction.followup.send(reply)

    @commands.command(name="core")
    async def core_command(self, ctx: commands.Context, *, message: str):
        reply = await self.ai_answer(message)
        await ctx.send(reply)


async def setup(bot: commands.Bot):
    await bot.add_cog(AICog(bot))
