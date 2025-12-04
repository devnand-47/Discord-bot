# cogs/fun.py

import random

import discord
from discord.ext import commands

MEMES = [
    "https://i.imgflip.com/30b1gx.jpg",
    "https://i.imgflip.com/1bij.jpg",
    "https://i.imgflip.com/26am.jpg",
]

EIGHTBALL = [
    "Yes.",
    "No.",
    "Maybe.",
    "Ask again later.",
    "Definitely.",
    "I doubt it.",
]


class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"Pong! `{round(self.bot.latency * 1000)} ms`")

    @commands.command(name="meme")
    async def meme(self, ctx: commands.Context):
        await ctx.send(random.choice(MEMES))

    @commands.command(name="8ball")
    async def eight_ball(self, ctx: commands.Context, *, question: str = ""):
        await ctx.send(f"🎱 {random.choice(EIGHTBALL)}")

    @commands.command(name="chat")
    async def chat(self, ctx: commands.Context, *, message: str):
        replies = [
            "Interesting...",
            "Tell me more.",
            "Why do you think that?",
            "Understood.",
            "Logged to neural core.",
        ]
        await ctx.send(random.choice(replies))


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
