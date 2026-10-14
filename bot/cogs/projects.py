import random

import aiohttp
import discord
import requests
from discord import app_commands
from discord.ext import commands
from thicc import thicc

from bot.helpers import tools


slot_values = [seven, eightball, dice, playingcard, cherry, moneybag, gold, diamond, dollar]

@commands.hybrid_command(description="Start the slot machine. Pay one token")
async def slotmachine(self, ctx: commands.Context, *, request: str):
  responses = [
    [
      print(random.choice(slot_values)) , print(random.choice(slot_values)) , print(random.choice(slot_values))
    ]
    # if all the values are same print you win. Else you lose. Not sure how to do this but whatever. This is the slot machine so far. Anyone else can update it
