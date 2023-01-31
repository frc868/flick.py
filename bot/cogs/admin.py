import logging
import subprocess

import discord
from discord.ext import commands

import bot.cogs.techhounds
from bot.helpers import tools


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.LoggerAdapter(
            logging.getLogger(__name__), {"botname": self.bot.name}
        )

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
            title="Pronouns",
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
    async def preparegradelevel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        embed = discord.Embed(
            title="Grade Level",
            description="Please select your grade level.",
            colour=discord.Colour.from_str("#FBBF05"),
        )

        await channel.send(
            embed=embed,
            view=bot.cogs.techhounds.create_persistent_grade_level_selector(
                self.bot.get_guild(403364109409845248)
            ),
        )

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: commands.Context, *, arg: str) -> None:
        await ctx.send(eval(arg))

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        await self.bot.tree.sync()
        await ctx.send("Synced application commands.")

    @commands.command()
    @commands.is_owner()
    async def gitpull(self, ctx: commands.Context) -> None:
        await ctx.send("Pulling from Git.")
        await ctx.send(
            subprocess.run(
                "git pull", shell=True, text=True, capture_output=True
            ).stdout
        )

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context) -> None:
        await ctx.send("Reloading bot.")
        self.logger.info("Reloading bot.")
        extensions = [name for name, extension in self.bot.extensions.items()]
        for extension in extensions:
            self.logger.info(f"Reloading {extension}.")
            await self.bot.reload_extension(extension)

        await ctx.send("Reloading complete.")

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx: commands.Context) -> None:
        await self.gitpull(ctx)
        await self.reload(ctx)

    @commands.command()
    @commands.is_owner()
    async def updatewebsite(self, ctx: commands.Context) -> None:
        await ctx.send("Pulling from Git.")
        await ctx.send(
            subprocess.run(
                "git pull",
                shell=True,
                text=True,
                capture_output=True,
                cwd="/opt/website",
            ).stdout
        )

        await ctx.send("Deploying to /var/www/html.")
        subprocess.run(
            "./deploy.sh",
            shell=True,
            text=True,
            capture_output=True,
            cwd="/home/dr",
        )
        await ctx.send("Deployed.")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        await self.bot.tree.sync()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
