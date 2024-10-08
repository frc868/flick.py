import discord
from discord import app_commands
from discord.ext import commands

from bot.helpers import tools
from datetime import datetime


class ModeratedChatView(discord.ui.View):
    users: list[discord.User]

    def __init__(self, users: list[discord.User]):
        self.users = users
        super().__init__(timeout=None)

    @discord.ui.button(label="Ping Adults", style=discord.ButtonStyle.blurple)
    async def pingadults(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        role = interaction.guild.get_role(1057724286837719041)
        await interaction.response.send_message(
            role.mention,
            embed=tools.create_embed(
                "Pinging adults",
                desc=f"{role.mention}, you have been pinged because someone requested that adults be notified about this conversation.",
            ),
        )

    @discord.ui.button(label="Close Channel", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        for user in self.users:
            perms = interaction.channel.overwrites_for(user)
            perms.send_messages = False
            perms.send_messages_in_threads = False
            await interaction.channel.set_permissions(user, overwrite=perms)
        await interaction.channel.edit(
            category=interaction.guild.get_channel(1139305639508721765)
        )

        embed = tools.create_embed(
            "Moderated Chat closed",
            desc=f"This chat between {self.users[0].mention} and {self.users[1].mention} has been closed. If you would like to continue this discussion at a later time, please create a new chat.",
        )
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(embed=embed)

        self.disable()
        try:
            await interaction.message.edit(view=self)
        except:
            pass

    def disable(self):
        for child in self.children:
            child.disabled = True
        self.stop()


class Moderation(commands.Cog):
    open_dms = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        description="Remove messages (optionally from a certain user)."
    )
    @app_commands.describe(
        num="The number of messages to remove.",
        user="The user from whom to remove messages.",
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(
        self, ctx: commands.Context, num: int, user: discord.User | None = None
    ):
        msgs = []
        async for msg in ctx.channel.history(limit=num, before=ctx.message):
            if not user or msg.author.id == user.id:
                msgs.append(msg)
        await ctx.channel.delete_messages(msgs)

        embed = tools.create_embed("Message Purge", f"{len(msgs)} messages deleted.")
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Start a moderated DM with another user.")
    async def moderatedchat(
        self, ctx: commands.Context, user: discord.User, subject: str
    ):
        category = ctx.guild.get_channel(1139007202166849566)  # moderated DMs category
        formatted_subject = subject[:20] if len(subject) >= 20 else subject

        channel = await category.create_text_channel(
            f"{datetime.now().replace(microsecond=0).strftime(r'%Y-%m-%d')}-{formatted_subject.lower().replace(' ', '-')}"
        )
        for u in [user, ctx.author]:
            perms = channel.overwrites_for(u)
            perms.view_channel = True
            await channel.set_permissions(u, overwrite=perms)
        embed = tools.create_embed(
            "Moderated Chat created",
            desc=f"{ctx.author.mention} created this channel to communicate with {user.mention}.\nViewable by coaches and leads.",
        )
        embed.add_field(name="Subject", value=subject)
        message: discord.Message = await channel.send(
            f"{ctx.author.mention} {user.mention}",
            embed=embed,
            view=ModeratedChatView([user, ctx.author]),
        )
        await message.pin()

        await ctx.send(
            embed=tools.create_embed(
                "", desc=f"Moderated Chat created: {channel.mention}"
            ),
            ephemeral=True,
        )

    @commands.hybrid_command(description="Start a moderated DM with another user.")
    async def chat(self, ctx: commands.Context, user: discord.User, subject: str):
        await self.moderatedchat(ctx, user, subject)

    # @purge.hybrid_command(name="user")
    # @commands.has_permissions(manage_messages=True)
    # @commands.bot_has_permissions(manage_messages=True)
    # async def purge_bots(self, ctx: commands.Context, num: int):
    #     moderation_record = await self.bot.db.fetchrow(
    #         "INSERT INTO moderations (server_id, type, moderator_id, channel, count) VALUES ($1, $2, $3, $4, $5) RETURNING *;",
    #         str(ctx.guild.id),
    #         "purge",
    #         str(ctx.author.id),
    #         str(ctx.channel.id),
    #         num,
    #     )
    #     msgs = []
    #     async for msg in ctx.channel.history(limit=num):
    #         if msg.author.bot:
    #             msgs.append(msg)
    #     await ctx.channel.delete_messages(msgs)

    #     embed = tools.create_embed(
    #         ctx, "Message Purge (Bots)", f"{num} messages deleted."
    #     )
    #     embed.add_field(
    #         name="moderation ID", value=moderation_record["id"], inline=False
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="purge",
    #     base_desc="Purge messages from the channel.",
    #     name="humans",
    #     description="Purge messages sent by humans.",
    #     options=[
    #         create_option(
    #             name="number",
    #             description="The number of messages to purge.",
    #             option_type=SlashCommandOptionType.INTEGER,
    #             required=True,
    #         ),
    #         create_option(
    #             name="reason",
    #             description="The reason for the purge.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=False,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(manage_messages=True)
    # @commands.bot_has_permissions(manage_messages=True)
    # async def purge_humans(self, ctx: SlashContext, number: int, reason: str):
    #     moderation_record = await self.bot.db.fetchrow(
    #         "INSERT INTO moderations (server_id, type, moderator_id, channel, count) VALUES ($1, $2, $3, $4, $5) RETURNING *;",
    #         str(ctx.guild.id),
    #         "purge",
    #         str(ctx.author.id),
    #         str(ctx.channel.id),
    #         number,
    #     )
    #     msgs = []
    #     async for msg in ctx.channel.history(limit=number):
    #         if not msg.author.bot:
    #             msgs.append(msg)
    #     await ctx.channel.delete_messages(msgs)

    #     embed = tools.create_embed(
    #         ctx, "Message Purge (Humans)", f"{number} messages deleted."
    #     )
    #     embed.add_field(
    #         name="Moderation ID", value=moderation_record["id"], inline=False
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_slash(
    #     name="warn",
    #     description="Warn a member of the server.",
    #     options=[
    #         create_option(
    #             name="user",
    #             description="The member to warn.",
    #             option_type=SlashCommandOptionType.USER,
    #             required=True,
    #         ),
    #         create_option(
    #             name="reason",
    #             description="The reason for the member's warn.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=False,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(manage_messages=True)
    # async def warn(
    #     self, ctx: SlashContext, user: discord.User, reason: str = None
    # ):
    #     moderation_record = await self.bot.db.fetchrow(
    #         "INSERT INTO moderations (server_id, type, user_id, moderator_id, reason) VALUES ($1, $2, $3, $4, $5) RETURNING *;",
    #         str(ctx.guild.id),
    #         "warn",
    #         str(user.id),
    #         str(ctx.author.id),
    #         reason,
    #     )
    #     embed = tools.create_embed("User Warn", desc=f"{user} has been warned.")
    #     embed.add_field(
    #         name="Moderation ID", value=moderation_record["id"], inline=False
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_slash(
    #     name="kick",
    #     description="Kick a member from the server.",
    #     options=[
    #         create_option(
    #             name="user",
    #             description="The member to kick.",
    #             option_type=SlashCommandOptionType.USER,
    #             required=True,
    #         ),
    #         create_option(
    #             name="reason",
    #             description="The reason for the member's kick.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=False,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(kick_members=True)
    # @commands.bot_has_permissions(kick_members=True)
    # async def kick(
    #     self, ctx: SlashContext, user: discord.User, reason: str = None
    # ):
    #     await ctx.guild.kick(user, reason=reason)
    #     moderation_record = await self.bot.db.fetchrow(
    #         "INSERT INTO moderations (server_id, type, user_id, moderator_id, reason) VALUES ($1, $2, $3, $4, $5) RETURNING *;",
    #         str(ctx.guild.id),
    #         "kick",
    #         str(user.id),
    #         str(ctx.author.id),
    #         reason,
    #     )
    #     embed = tools.create_embed("User Kick", desc=f"{user} has been kicked.")
    #     embed.add_field(
    #         name="Moderation ID", value=moderation_record["id"], inline=False
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_slash(
    #     name="ban",
    #     description="Ban a member from the server.",
    #     options=[
    #         create_option(
    #             name="user",
    #             description="The member to ban.",
    #             option_type=SlashCommandOptionType.USER,
    #             required=True,
    #         ),
    #         create_option(
    #             name="reason",
    #             description="The reason for the member's ban.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=False,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(ban_members=True)
    # @commands.bot_has_permissions(ban_members=True)
    # async def ban(
    #     self, ctx: SlashContext, user: discord.User, reason: str = None
    # ):
    #     await ctx.guild.ban(user, reason=reason)
    #     moderation_record = await self.bot.db.fetchrow(
    #         "INSERT INTO moderations (server_id, type, user_id, moderator_id, reason) VALUES ($1, $2, $3, $4, $5) RETURNING *;",
    #         str(ctx.guild.id),
    #         "ban",
    #         str(user.id),
    #         str(ctx.author.id),
    #         reason,
    #     )
    #     embed = tools.create_embed("User Ban", desc=f"{user} has been banned.")
    #     embed.add_field(
    #         name="Moderation ID", value=moderation_record["id"], inline=False
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_slash(
    #     name="mute",
    #     description="Mute a user from the server.",
    #     options=[
    #         create_option(
    #             name="user",
    #             description="The user to mute.",
    #             option_type=SlashCommandOptionType.USER,
    #             required=True,
    #         ),
    #         create_option(
    #             name="duration",
    #             description="The duration of the mute. Use 0 for a manual unmute.",
    #             option_type=SlashCommandOptionType.INTEGER,
    #             required=True,
    #         ),
    #         create_option(
    #             name="duration_unit",
    #             description="The unit of time for the duration.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=True,
    #             choices=[
    #                 create_choice(name="days", value="days"),
    #                 create_choice(name="hours", value="hours"),
    #                 create_choice(name="minutes", value="minutes"),
    #                 create_choice(name="seconds", value="seconds"),
    #             ],
    #         ),
    #         create_option(
    #             name="reason",
    #             description="The reason for the member's mute.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=False,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(manage_roles=True)
    # @commands.bot_has_permissions(manage_roles=True)
    # async def mute(
    #     self,
    #     ctx: SlashContext,
    #     user: discord.User,
    #     duration: int,
    #     duration_unit: str,
    #     reason: str = None,
    # ):
    #     await user.add_roles(ctx.guild.get_role(809169133232717890))
    #     duration_adjustments = {
    #         "days": 1 * 60 * 60 * 24,
    #         "hours": 1 * 60 * 60,
    #         "minutes": 1 * 60,
    #         "seconds": 1,
    #     }
    #     adjusted_duration = duration * duration_adjustments[duration_unit]
    #     moderation_record = await self.bot.db.fetchrow(
    #         "INSERT INTO moderations (server_id, type, user_id, moderator_id, reason, duration, active) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *;",
    #         str(ctx.guild.id),
    #         "mute",
    #         str(user.id),
    #         str(ctx.author.id),
    #         reason,
    #         adjusted_duration,
    #         True,
    #     )
    #     embed = tools.create_embed("User Mute", desc=f"{user} has been muted.")
    #     embed.add_field(
    #         name="Moderation ID", value=moderation_record["id"], inline=False
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_slash(
    #     name="unmute",
    #     description="Unmute a member from the server.",
    #     options=[
    #         create_option(
    #             name="member",
    #             description="The member to unmute.",
    #             option_type=SlashCommandOptionType.USER,
    #             required=True,
    #         ),
    #         create_option(
    #             name="reason",
    #             description="The reason for the member's unmute.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=False,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(manage_roles=True)
    # @commands.bot_has_permissions(manage_roles=True)
    # async def unmute(self, ctx: SlashContext, user: discord.User, reason=None):
    #     moderation_record = await self.bot.db.fetchrow(
    #         "INSERT INTO moderations (server_id, type, user_id, moderator_id, reason) VALUES ($1, $2, $3, $4, $5) RETURNING *;",
    #         str(ctx.guild.id),
    #         "unmute",
    #         str(user.id),
    #         str(ctx.author.id),
    #         reason,
    #     )
    #     await user.remove_roles(ctx.guild.get_role(809169133232717890))
    #     embed = tools.create_embed("User Unmute", desc=f"{user} has been unmuted.")
    #     embed.add_field(
    #         name="Moderation ID", value=moderation_record["id"], inline=False
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="moderations",
    #     base_desc="Get moderations registered with the bot.",
    #     subcommand_group="list",
    #     sub_group_desc="Get a list of moderations registered with the bot.",
    #     name="all",
    #     description="Get a list of all moderations in the server.",
    # )
    # @commands.has_permissions(manage_messages=True)
    # async def moderations_list_server(self, ctx: SlashContext):
    #     records = await self.bot.db.fetch(
    #         "SELECT * FROM moderations WHERE server_id=$1", str(ctx.guild.id)
    #     )
    #     embeds = []
    #     number_of_pages = -(len(records) // -10)
    #     for num in range(number_of_pages):
    #         embeds.append(
    #             tools.create_embed(
    #                 ctx,
    #                 f"Server Moderations (Page {num + 1}/{number_of_pages})",
    #                 desc=f"Found {len(records)} records.",
    #             )
    #         )
    #     for index, record in enumerate(records):
    #         user = await self.bot.fetch_user(record["user_id"])
    #         val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
    #         embeds[index // 10].add_field(name=record["id"], value=val, inline=False)
    #     paginator = tools.EmbedPaginator(self.bot, ctx, embeds)
    #     await paginator.run()

    # @cog_ext.cog_subcommand(
    #     base="moderations",
    #     base_desc="Get moderations registered with the bot.",
    #     subcommand_group="list",
    #     sub_group_desc="Get moderations registered with the bot.",
    #     name="user",
    #     description="Get a list of moderations for a user in the server.",
    #     options=[
    #         create_option(
    #             name="user",
    #             description="The user to get the moderations of.",
    #             option_type=SlashCommandOptionType.USER,
    #             required=True,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(manage_messages=True)
    # async def moderations_list_user(
    #     self, ctx: SlashContext, user: discord.User
    # ):
    #     records = await self.bot.db.fetch(
    #         "SELECT * FROM moderations WHERE server_id=$1 AND user_id=$2;",
    #         str(ctx.guild.id),
    #         str(user.id),
    #     )
    #     embeds = []
    #     number_of_pages = -(len(records) // -10)
    #     for num in range(number_of_pages):
    #         embeds.append(
    #             tools.create_embed(
    #                 ctx,
    #                 f"Server Moderations (Page {num + 1}/{number_of_pages})",
    #                 desc=f"Filtering by user {user.mention}. Found {len(records)} records.",
    #             )
    #         )
    #     for index, record in enumerate(records):
    #         user = await self.bot.fetch_user(record["user_id"])
    #         val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
    #         embeds[index // 10].add_field(name=record["id"], value=val, inline=False)
    #     paginator = tools.EmbedPaginator(self.bot, ctx, embeds)
    #     await paginator.run()

    # @cog_ext.cog_subcommand(
    #     base="moderations",
    #     base_desc="Get moderations registered with the bot.",
    #     subcommand_group="list",
    #     sub_group_desc="Get a list of moderations registered with the bot.",
    #     name="type",
    #     description="Get a list of all moderations in the server.",
    #     options=[
    #         create_option(
    #             name="type",
    #             description="The type of moderation to search for.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=True,
    #             choices=[
    #                 create_choice(
    #                     name="mute",
    #                     value="mute",
    #                 ),
    #                 create_choice(
    #                     name="unmute",
    #                     value="unmute",
    #                 ),
    #                 create_choice(
    #                     name="warn",
    #                     value="warn",
    #                 ),
    #                 create_choice(
    #                     name="kick",
    #                     value="kick",
    #                 ),
    #                 create_choice(
    #                     name="ban",
    #                     value="ban",
    #                 ),
    #                 create_choice(
    #                     name="unban",
    #                     value="unban",
    #                 ),
    #                 create_choice(
    #                     name="purge",
    #                     value="purge",
    #                 ),
    #             ],
    #         ),
    #     ],
    # )
    # @commands.has_permissions(manage_messages=True)
    # async def moderations_list_type(self, ctx: SlashContext, type: str):
    #     records = await self.bot.db.fetch(
    #         "SELECT * FROM moderations WHERE server_id=$1 AND type=$2;",
    #         str(ctx.guild.id),
    #         type,
    #     )
    #     embeds = []
    #     number_of_pages = -(len(records) // -10)
    #     for num in range(number_of_pages):
    #         embeds.append(
    #             tools.create_embed(
    #                 ctx,
    #                 f"Server Moderations (Page {num + 1}/{number_of_pages})",
    #                 desc=f"Filtering by type {type}. Found {len(records)} records.",
    #             )
    #         )
    #     for index, record in enumerate(records):
    #         user = await self.bot.fetch_user(record["user_id"])
    #         val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
    #         embeds[index // 10].add_field(name=record["id"], value=val, inline=False)
    #     paginator = tools.EmbedPaginator(self.bot, ctx, embeds)
    #     await paginator.run()

    # @cog_ext.cog_subcommand(
    #     base="moderations",
    #     base_desc="Get moderations registered with the bot.",
    #     name="info",
    #     description="Get a info on a specific moderation.",
    #     options=[
    #         create_option(
    #             name="id",
    #             description="The unique ID associated with the moderation.",
    #             option_type=SlashCommandOptionType.STRING,
    #             required=True,
    #         ),
    #     ],
    # )
    # @commands.has_permissions(manage_messages=True)
    # async def moderations_info(self, ctx: SlashContext, id: str):
    #     record = await self.bot.db.fetchrow(
    #         "SELECT * FROM moderations WHERE server_id=$1 AND id=$2;",
    #         str(ctx.guild.id),
    #         id,
    #     )
    #     if not record:
    #         embed = tools.create_error_embed(
    #             ctx, "Moderation not found. Please check the ID you gave."
    #         )
    #         await ctx.send(embed=embed)
    #     else:
    #         embed = tools.create_embed("Moderation Info")
    #         embed.add_field(name="ID", value=record["id"])
    #         embed.add_field(name="Type", value=record["type"])
    #         if record["duration"]:
    #             embed.add_field(
    #                 name="Duration",
    #                 value=time.strftime(
    #                     "%Mm %Ss", time.gmtime(round(record["duration"]))
    #                 ),
    #             )
    #         embed.add_field(
    #             name="Offender",
    #             value=ctx.guild.get_member(int(record["user_id"])).mention,
    #         )
    #         embed.add_field(
    #             name="Punisher",
    #             value=ctx.guild.get_member(int(record["moderator_id"])).mention,
    #         )
    #         embed.add_field(
    #             name="Date",
    #             value=record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p"),
    #         )
    #         if record["reason"]:
    #             embed.add_field(name="Reason", value=record["reason"])
    #         else:
    #             embed.add_field(name="Reason", value="None")
    #         await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
