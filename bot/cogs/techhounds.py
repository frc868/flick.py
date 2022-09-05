import discord
from discord import app_commands
from discord.ext import commands

from bot.helpers import tools


class NameModal(discord.ui.Modal, title="Name"):
    name = discord.ui.TextInput(label="Enter your name (first last)")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            first_name, last_name = self.name.value.split()
            formatted_name = f"{first_name.title()} {last_name[0].upper()}"
        except:
            await interaction.response.send_message(
                embed=tools.create_error_embed(
                    'Could not normalize name. Please write your name in the form "FIRSTNAME LASTNAME".'
                ),
                ephemeral=True,
            )
            return
        try:
            await interaction.user.edit(nick=formatted_name)
            await interaction.response.send_message(
                embed=tools.create_embed(
                    "Set Name", f"Set your nickname to {formatted_name}."
                ),
                ephemeral=True,
            )
        except:
            await interaction.response.send_message(
                embed=tools.create_error_embed(
                    "Could not set your nickname. Please ping a lead."
                ),
                ephemeral=True,
            )


class NameView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Set Name", custom_id="nickname")
    async def name(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = NameModal()
        await interaction.response.send_modal(modal)


def create_persistent_division_selector(
    guild: discord.Guild,
) -> tools.PersistentRoleSelector:
    return tools.PersistentRoleSelector(
        guild,
        [
            403694370135605249,
            403694172814573595,
            403694622544494593,
            403694722759131138,
            451039138100281344,
        ],
        "Division",
        custom_id_prefix="division",
    )


def create_persistent_pronoun_selector(
    guild: discord.Guild,
) -> tools.PersistentRoleSelector:
    return tools.PersistentRoleSelector(
        guild,
        [
            663862448159326209,
            663862473891512370,
            663862492698640384,
        ],
        "Pronouns",
        custom_id_prefix="pronoun",
    )

def create_persistent_grade_level_selector(
    guild: discord.Guild,
) -> tools.PersistentRoleSelector:
    return tools.PersistentRoleSelector(
        guild,
        [
            1014547797132972052,
            1014547916473503885,
            1014547950397034617,
            1014547985348186284
        ],
        "Grade Level",
        custom_id_prefix="gradelevel",
    )


class TechHounds(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Set your division.")
    async def division(self, ctx: commands.Context) -> None:
        view = tools.RoleSelector(
            ctx.author,
            ctx.guild,
            [
                403694370135605249,
                403694172814573595,
                403694622544494593,
                403694722759131138,
                451039138100281344,
            ],
            "Division Selector",
        )
        view.msg = await ctx.send(
            embed=tools.create_embed(
                "Division Selector",
                "Please select the division you would like to join.",
            ),
            view=view,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TechHounds(bot))
