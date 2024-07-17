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

    def admin_access(ctx: commands.Context) -> bool:
        lead = 650166283211636746
        mentor = 1224052980857311245

        return ctx.author.id in [lead, mentor]

    @commands.command()
    @commands.check(admin_access)
    async def preparedivision(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
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
    @commands.check(admin_access)
    async def preparename(self, ctx: commands.Context, channel: discord.TextChannel):
        embed = discord.Embed(
            title="Nickname",
            description="Please press the button below to set your nickname.",
            colour=discord.Colour.from_str("#FBBF05"),
        )

        await channel.send(embed=embed, view=bot.cogs.techhounds.NameView())

    @commands.command()
    @commands.check(admin_access)
    async def preparepronoun(self, ctx: commands.Context, channel: discord.TextChannel):
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
    @commands.check(admin_access)
    async def preparegradelevel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
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
    @commands.check(admin_access)
    async def eval(self, ctx: commands.Context, *, arg: str):
        await ctx.send(eval(arg))

    @commands.command()
    @commands.check(admin_access)
    async def sync(self, ctx: commands.Context):
        await self.bot.tree.sync()
        await ctx.send("Synced application commands.")

    @commands.command()
    @commands.check(admin_access)
    async def gitpull(self, ctx: commands.Context):
        await ctx.send("Pulling from Git.")
        await ctx.send(
            subprocess.run(
                "git pull", shell=True, text=True, capture_output=True
            ).stdout
        )

    @commands.command()
    @commands.check(admin_access)
    async def reload(self, ctx: commands.Context):
        await ctx.send("Reloading bot.")
        self.logger.info("Reloading bot.")
        extensions = [name for name, extension in self.bot.extensions.items()]
        for extension in extensions:
            self.logger.info(f"Reloading {extension}.")
            await self.bot.reload_extension(extension)

        await ctx.send("Reloading complete.")

    @commands.command()
    @commands.check(admin_access)
    async def update(self, ctx: commands.Context):
        await self.gitpull(ctx)
        await self.reload(ctx)

    @commands.command()
    @commands.check(admin_access)
    async def updatewebsite(self, ctx: commands.Context):
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
        await ctx.send(
            subprocess.run(
                "git pull",
                shell=True,
                text=True,
                capture_output=True,
                cwd="/opt/website-dev",
            ).stdout
        )

        await ctx.send("Deploying to /var/www/html and /var/www/dev.")
        subprocess.run(
            "./deploy.sh",
            shell=True,
            text=True,
            capture_output=True,
            cwd="/home/davidracovan",
        )
        await ctx.send("Deployed.")

    @commands.command()
    @commands.check(admin_access)
    async def sync(self, ctx: commands.Context):
        await self.bot.tree.sync()
        await ctx.send("Synced.")

    @commands.command()
    @commands.check(admin_access)
    async def cycleyearroles(self, ctx: commands.Context):
        class Roles:
            freshman = 1014547797132972052
            sophomore = 1014547916473503885
            junior = 1014547950397034617
            senior = 1014547985348186284

        def check(msg):
            return (
                msg.author == ctx.author
                and msg.channel == ctx.channel
                and msg.content.lower() in ["y", "n"]
            )

        async def ask():
            msg = await self.bot.wait_for("message", check=check)
            if msg.content.lower() == "y":
                return True
            else:
                return False

        for message, old_role_id, new_role_id in [
            (
                "Transition year roles up for juniors? (y/n)",
                Roles.junior,
                Roles.senior,
            ),
            (
                "Transition year roles up for sophomores? (y/n)",
                Roles.sophomore,
                Roles.junior,
            ),
            (
                "Transition year roles up for freshmen? (y/n)",
                Roles.freshman,
                Roles.sophomore,
            ),
        ]:
            await ctx.send(message)
            resp = await ask()
            if resp:
                old_role = ctx.guild.get_role(old_role_id)
                new_role = ctx.guild.get_role(new_role_id)
                for member in old_role.members:
                    await member.add_roles(new_role)
                    await member.remove_roles(old_role)
            else:
                await ctx.send("Stopping.")
                return


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
