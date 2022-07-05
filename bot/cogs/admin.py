import asyncio
import random

import aiohttp
import discord
from discord.ext import commands

import bot.cogs.techhounds
from bot.helpers import tools


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def preparedivision(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        embed = discord.Embed(
            title="Division",
            description="Please select the division you would like to join.",
            colour=discord.Colour.from_str("#FBBF05"),
        )

        await channel.send(
            embed=embed,
            view=bot.cogs.techhounds.create_persistent_division_selector(
                self.bot.get_guild(403364109409845248)
            ),
        )

    @commands.command()
    @commands.is_owner()
    async def preparename(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        embed = discord.Embed(
            title="Nickname",
            description="Please press the button below to set your nickname.",
            colour=discord.Colour.from_str("#FBBF05"),
        )

        await channel.send(embed=embed, view=bot.cogs.techhounds.NameView())

    @commands.command()
    @commands.is_owner()
    async def preparepronoun(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        embed = discord.Embed(
            title="Division",
            description="Please select your pronouns if you feel comfortable doing so.",
            colour=discord.Colour.from_str("#FBBF05"),
        )

        await channel.send(
            embed=embed,
            view=bot.cogs.techhounds.create_persistent_pronoun_selector(
                self.bot.get_guild(403364109409845248)
            ),
        )

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: commands.Context, *, arg: str) -> None:
        await ctx.send(eval(arg))

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Synced application commands.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
