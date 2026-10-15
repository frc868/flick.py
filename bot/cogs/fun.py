import random

import aiohttp
import discord
import requests
import xkcd
from discord import app_commands
from discord.ext import commands
from thicc import thicc

from bot.helpers import tools


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Greet the bot!", aliases=["hi"])
    async def hello(self, ctx: commands.Context):
        await ctx.send(
            embed=tools.create_embed(
                "Hello!", desc=f"How are you, {ctx.author.mention}?"
            )
        )

    @commands.hybrid_command(description="Ask the ~~magic~~ 8 Ball a question.")
    async def eightball(self, ctx: commands.Context, *, request: str):
        responses = [
            [
                "🟢 As I see it, yes. 🟢",
                "🟢 It is certain. 🟢",
                "🟢 It is decidedly so. 🟢",
                "🟢 Most likely. 🟢",
                "🟢 Outlook good. 🟢",
                "🟢 Signs point to yes. 🟢",
                "🟢 Without a doubt. 🟢",
                "🟢 Yes. 🟢",
                "🟢 Yes, definitely. 🟢",
                "🟢 You may rely on it. 🟢",
            ],
            [
                "🔴 Very doubtful. 🔴",
                "🔴 My reply is no. 🔴",
                "🔴 My sources say no. 🔴",
                "🔴 Outlook not so good. 🔴",
                "🔴 Don't count on it. 🔴",
            ],
            [
                "🟡 Ask again later. 🟡",
                "🟡 Better not tell you now. 🟡",
                "🟡 Cannot predict now. 🟡",
                "🟡 Concentrate and ask again. 🟡",
                "🟡 Reply hazy, try again. 🟡",
            ],
        ]

        rand_int = random.randint(1, 5)
        if rand_int in [1, 2]:
            response_category = responses[0]
        elif rand_int in [3, 4]:
            response_category = responses[1]
        else:
            response_category = responses[2]

        if ("lying" in request.lower()) or ("lie" in request.lower()):
            response = (
                "🟢 🟡 🔴 How dare you! The magical 8 ball never lies! Shame on you! 🔴 🟡 🟢"
            )
        else:
            response = response_category[random.randint(0, len(response_category) - 1)]
        embed = tools.create_embed("Magic 8 Ball")
        embed.add_field(name="Request", value=request, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.send(embed=embed)


    @commands.hybrid_command(description="Go fishing 🎣")
    async def fishing(self, ctx: commands.Context):
        adjs = [
            "red",
            "blue",
            "green",
            "yellow",
            "big",
            "small",
            "long",
            "short",
            "hot",
            "cold",
            "fast",
            "slow",
            "heavy",
            "light",
            "loud",
            "quiet",
            "hard",
            "soft",
            "smooth",
            "rough",
            "thick",
            "thin",
            "sharp",
            "dull",
            "bright",
            "dark",
            "clean",
            "dirty",
            "shiny",
            "rusty",
            "wet",
            "dry",
            "sticky",
            "slimy",
            "greasy",
            "fuzzy",
            "hairy",
            "bald",
            "striped",
            "dotted",
            "purple",
            "orange",
            "pink",
            "turquoise",
            "magenta",
            "beige",
            "neon",
            "transparent",
            "metallic",
            "wooden",
            "plastic",
            "rubber",
            "cardboard",
            "rectangular",
            "triangular",
            "spherical",
            "crooked",
            "diagonal",
            "asymmetrical",
            "automatic",
            "digital",
            "analog",
            "electric",
            "acoustic",
            "portable",
            "cordless",
            "waterproof",
            "rechargeable",
            "synthetic",
            "organic",
            "industrial",
            "domestic",
            "commercial",
            "agricultural",
            "municipal",
            "maritime",
            "aerodynamic",
            "microscopic",
            "telescopic",
            "barometric",
            "chronological",
            "geological",
            "biochemical",
            "thermodynamic",
            "electromagnetic",
            "bureaucratic",
            "gothic",
            "medieval",
            "prehistoric",
            "parabolic",
            "orthogonal",
            "concentric",
            "diagonal",
            "steganographic",
            "cryptographic",
            "claustrophobic",
            "uncomfortable",
            "expensive",
            "fragile",
            "flammable",
            "radioactive",
            "biodegradable",
            "edible",
            "poisonous",
            "stinky",
            "perfumed",
            "tasty",
            "bitter",
            "sour",
            "salty",
            "spicy",
            "crunchy",
            "chewy",
            "soggy",
            "stale",
            "frozen",
            "melted",
            "rotten",
            "moldy",
            "hollow",
            "inflated",
            "deflated",
            "cluttered",
            "spacious",
            "crooked",
            "wobbly",
            "elastic",
            "brittle",
            "porous",
            "dense",
            "holographic",
            "supersonic",
            "radioactive",
            "quantum",
            "cybernetic",
            "bionic",
            "magnetic",
            "fluorescent",
            "phosphorescent",
            "pixelated",
            "glitched",
            "automated",
            "simulated",
            "synthetic",
            "supersonic",
            "interstellar",
            "subatomic",
            "nano-sized",
            "bio-engineered",
            "crusty",
            "dusty",
            "chunky",
            "lumpy",
            "greasy",
            "mushy",
            "rubbery",
            "spiky",
            "pointy",
            "bumpy",
            "squishy",
            "springy",
            "leaky",
            "rusty",
            "moldy",
            "cracked",
            "dented",
            "smelly",
            "damp",
            "soggy",
            "greasy",
            "gooey",
            "chunky",
            "clumpy",
            "fluffy",
            "sparkly",
            "glittery",
            "glow-in-the-dark",
            "high-definition",
            "overpriced",
            "low-budget",
            "bootleg",
            "counterfeit",
            "vintage",
            "retro",
            "futuristic",
            "cyberpunk",
            "steampunk",
            "clunky",
            "janky",
            "wonky",
            "goofy",
            "wobbly",
            "derpy",
            "chonky",
            "stinky",
            "smelly",
            "dummy-thick",
            "beefy",
            "juicy",
            "crispy",
            "saucy",
            "spicy",
            "funky",
            "groovy",
            "sketchy",
            "sus",
            "glitched",
            "cursed",
            "blessed",
            "haunted",
            "possessed",
            "radioactive",
            "toxic",
            "mutant",
            "cyborg",
            "robot-controlled",
            "laser-guided",
            "turbo-charged",
            "rocket-powered",
            "nuclear",
            "atomic",
            "cosmic",
            "interdimensional",
            "tactical",
            "military-grade",
            "heavy-duty",
            "industrial-strength",
            "bulletproof",
            "waterproof",
            "fireproof",
            "foolproof",
            "explosion-proof",
            "illegal",
            "forbidden",
            "secret",
            "classified",
            "invisible",
            "intangible",
            "immortal",
            "infinite",
            "microscopic",
            "gargantuan",
            "colossal",
            "gigantic",
            "titanic",
            "omega-level",
            "alpha",
            "beta",
            "noobish",
            "god-tier",
            "legendary",
            "mythical",
            "ancient",
            "prehistoric",
            "caveman-like",
            "roman-empire-style",
            "medieval",
            "renaissance",
            "victorian",
            "pirate-themed",
            "space-age",
            "cyber",
            "digital",
            "virtual",
            "holographic",
            "metaversal",
            "crypto-backed",
            "ai-generated",
            "deepfaked",
            "photoshop-fail",
            "clickbait",
            "trending",
            "viral",
            "cringe",
            "based",
            "edgy",
            "emo",
            "goth",
            "hypebeast",
            "boujee",
            "fancy",
            "luxurious",
            "extravagant",
            "golden",
            "diamond-encrusted",
            "platinum",
            "solid-gold",
            "plastic-wrap-covered",
            "cardboard",
            "duct-taped",
            "velcro-attached",
            "bubble-wrap-wrapped",
            "spatula-shaped",
            "toaster-fresh",
            "hot-dog-scented",
            "shrek-green",
            "gengis-khan-approved",
            "darth-vader-black",
            "spiderman-colored",
            "santa-claus-red"
        ]

        nouns = [
            "water",
            "book",
            "hand",
            "eye",
            "car",
            "house",
            "phone",
            "table",
            "chair",
            "door",
            "paper",
            "money",
            "food",
            "dog",
            "tree",
            "key",
            "shoe",
            "bed",
            "bag",
            "window",
            "computer",
            "cup",
            "pen",
            "clock",
            "shirt",
            "box",
            "hat",
            "bottle",
            "knife",
            "spoon",
            "glass",
            "plate",
            "desk",
            "cat",
            "bicycle",
            "coat",
            "lamp",
            "wallet",
            "pillow",
            "mirror",
            "blanket",
            "soap",
            "towel",
            "hammer",
            "coin",
            "guitar",
            "camera",
            "backpack",
            "umbrella",
            "suitcase",
            "screwdriver",
            "ladder",
            "candle",
            "scissors",
            "calendar",
            "flashlight",
            "thermostat",
            "calculator",
            "clipboard",
            "extension-cord",
            "tarp",
            "microscope",
            "stethoscope",
            "barometer",
            "telegraph",
            "oscilloscope",
            "theodolite",
            "goniometer",
            "dynamometer",
            "planimeter",
            "caliper",
            "sextant",
            "octant",
            "retort",
            "speculum",
            "slide-rule",
            "plumb-bob",
            "briefcase",
            "magnifier",
            "binoculars",
            "hourglass",
            "compass",
            "telescope",
            "globe",
            "sculpture",
            "microphone",
            "lantern",
            "violin",
            "spindle",
            "quill",
            "propeller",
            "gavel",
            "metronome",
            "astrolabe",
            "abacus",
            "phonograph",
            "alembic",
            "monocle",
            "centrifuge",
            "crucible",
            "biretta",
            "visor",
            "sledgehammer",
            "anvil",
            "pendulum",
            "sundial",
            "chisel",
            "gargoyle",
            "golem",
            "poltergeist",
            "doppelganger",
            "phoenix",
            "pegasus",
            "banshee",
            "aristotle",
            "isaac-newton",
            "albert-einstein",
            "marie-curie",
            "confucius",
            "marco-polo",
            "william-shakespeare",
            "leonardo-da-vinci",
            "alexander-the-great",
            "julius-caesar",
            "cleopatra",
            "queen-victoria",
            "abraham-lincoln",
            "joan-of-arc",
            "king-tut",
            "napoleon",
            "velcro",
            "paperclip",
            "zipper",
            "keychain",
            "cardboard",
            "bubble-wrap",
            "duct-tape",
            "manhole-cover",
            "stapler",
            "shoelace",
            "toothbrush",
            "pillowcase",
            "corkscrew",
            "tweezer",
            "coaster",
            "harmonica",
            "kazoo",
            "fly-swatter",
            "wind-chime",
            "bungee-cord",
            "thimble",
            "tuning-fork",
            "weather-vane",
            "shoehorn",
            "straight-jacket",
            "phonograph-needle",
            "avatar",
            "cloud-computing",
            "biofuel",
            "cyber-attack",
            "pixel",
            "algorithm",
            "metaverse",
            "teleporter",
            "exoskeleton",
            "hover-craft",
            "hologram",
            "jet-pack",
            "laser-pointer",
            "time-machine",
            "plasma-rifle",
            "space-elevator",
            "dyson-sphere",
            "shrink-ray",
            "rail-gun",
            "portal-gun",
            "warp-drive",
            "flux-capacitor",
            "sonic-screwdriver",
            "matter-replicator",
            "smart-watch",
            "drone",
            "nanobot",
            "deepfake",
            "crypto",
            "blockchain",
            "hoverboard",
            "podcast",
            "vlogger",
            "glitch",
            "fidget-spinner",
            "emoji",
            "hashtag",
            "clickbait",
            "meme",
            "selfie",
            "air-fryer",
            "spatula",
            "toaster",
            "spork",
            "noob",
            "roman-empire",
            "sherlock-holmes",
            "harry-potter",
            "tarzan",
            "dracula",
            "santa-claus",
            "spiderman",
            "george-washington",
            "darth-vader",
            "gengis-khan",
            "shrek",
            "hot-dog",
            "vedanth"
        ]

        fish = ""
        totalrarity = 0

        for i in range(random.randint(1, 3)):
            rarity = random.randint(0,len(adjs)-1)
            fish += adjs[rarity] + " "
            totalrarity += rarity

        rarity = random.randint(0,len(nouns)-1)
        fish += nouns[rarity] + "fish."
        totalrarity += rarity

        totalrarity /= (3 * len(adjs) + len(nouns) - 4)

        color = "30"

        if(totalrarity) > 0.2:
            color = "32"
        if(totalrarity) > 0.4:
            color = "36"
        if(totalrarity) > 0.6:
            color = "35"
        if(totalrarity) > 0.8:
            color = "33"
        
        embed = tools.create_embed("Lake")
        embed.add_field(name="fish", value=f"```ansi\nYou caught a \u001b[0;{color}m{fish}\u001b[0m\n```", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        description="Get a random number in a specified range (inclusive)."
    )
    @app_commands.describe(
        min_num="The minimum number in the range.",
        max_num="The maximum number in the range.",
    )
    @commands.cooldown(1, 10)
    async def rng(self, ctx: commands.Context, min_num: int, max_num: int):
        embed = tools.create_embed(
            "Random Number", desc=f"```{random.randint(min_num, max_num)}```"
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get a dog picture!")
    @commands.cooldown(1, 3)
    async def dog(self, ctx: commands.Context):
        """Get a dog picture!"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed("Doggo!")
                    embed.set_image(url=js["message"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get a cat picture!")
    @commands.cooldown(1, 3)
    async def cat(self, ctx: commands.Context):
        """Get a cat picture!"""
        async with aiohttp.ClientSession() as session:
            async with session.get("http://aws.random.cat/meow") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed("Cat!")
                    embed.set_image(url=js["file"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name="xkcd", description="Launch an XKCD browser.")
    async def xkcd_(self, ctx: commands.Context, num: int | None = None):
        def callback(page: int) -> discord.Embed:
            comic = xkcd.getComic(page + 1)
            embed = tools.create_embed(f"XKCD {page+1}: {comic.getTitle()}")
            embed.set_image(url=comic.getImageLink())
            embed.add_field(name="Alt Text", value=comic.getAltText())
            return embed

        page_idx = num - 1 if num else xkcd.getLatestComicNum() - 1
        view = tools.EmbedButtonPaginator(
            ctx.author, [None] * xkcd.getLatestComicNum(), page_idx, callback
        )
        view.msg = await ctx.send(
            embed=callback(page_idx),
            view=view,
        )

    @commands.hybrid_command(description="Makes text look aesthetic.")
    @app_commands.describe(text="The text to make look aesthetic.")
    async def aes(self, ctx: commands.Context, *, text: str):
        await ctx.send(thicc.map_string(text))

    @commands.hybrid_command(
        description="Makes text look aesthetic but less cool than aes."
    )
    @app_commands.describe(text="The text to make look aesthetic.")
    async def pooraes(self, ctx: commands.Context, *, text: str):
        await ctx.send(" ".join(text))

    @commands.hybrid_command(description="Clapping.")
    @app_commands.describe(text="The text to clapify.")
    async def clap(self, ctx: commands.Context, *, text: str):
        await ctx.send("👏".join(text.split()) if len(text.split()) > 1 else f"👏{text}👏")

    @commands.hybrid_command(description="Clapping but with a custom separator.")
    @app_commands.describe(
        separator="The text to use instead of a clap.", text="The text to clapify."
    )
    async def clapwith(self, ctx: commands.Context, separator: str, *, text: str):
        await ctx.send(
            separator.join(text.split())
            if len(text.split()) > 1
            else f"{separator}{text}{separator}"
        )

    @commands.hybrid_command(description="Get a dad joke.")
    async def dad(self, ctx: commands.Context):
        await ctx.send(
            embed=tools.create_embed(
                "~~bad~~ dad joke",
                desc=requests.get(
                    "https://icanhazdadjoke.com/", headers={"Accept": "text/plain"}
                ).content.decode(),
            )
        )

    @commands.hybrid_command(
        description="Make text dance. Text must be three characters long."
    )
    @app_commands.describe(
        text="The text to make dance. Must be three characters long."
    )
    async def dance(
        self, ctx: commands.Context, text: str = "uwu"
    ):  # TODO: make this work with other text lengths because why not
        arg = text if len(text) == 3 else "uwu"
        await ctx.send(f"{arg[0]}{arg[1]} {arg[2]}\n{arg[0]} {arg[1]}{arg[2]}\n" * 3)

    @commands.hybrid_command(description="Mock something.")
    @app_commands.describe(text="The text to mock.")
    async def mock(self, ctx: commands.Context, *, text: str):
        await ctx.send(
            "".join(
                [x.lower() if i % 2 == 0 else x.upper() for i, x in enumerate(text)]
            )
        )

    @commands.hybrid_command(description="Flip a coin!")
    async def coin(self, ctx: commands.Context):
        await ctx.send(
            embed=tools.create_embed("Coin Flip", random.choice(["Heads!", "Tails!"]))
        )

    @commands.hybrid_command(description="Where's my wago?")
    @app_commands.describe(member="The person to ping.")
    async def wago(self, ctx: commands.Context, member: discord.Member | None = None):
        await ctx.send(
            (
                member.mention
                if member
                else random.choice(
                    [
                        member
                        for member in ctx.guild.members
                        if member.status == discord.Status.online
                    ]
                ).mention
            )
            + " Where's my wago?"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
