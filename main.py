# axo by kenyzin

import discord
import time
import random
import logging
import aiohttp
import sys
import traceback
import sqlite3
import asyncio
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.ext.commands import command
import discord.errors
import discord.ext
from tabulate import tabulate
from discord.utils import find
from functools import partial

startup_extensions = ["cogs.axomusic", "cogs.othercommands"]

bot = commands.Bot(command_prefix="?")
bot.remove_command('help')

missingargu = """:x: **Missing Argument** \n
Argument List: \n
**Music Commands:**
```
?play     <song_name>
?volume   <size>
?join     <channel_name>
```
**Other Commands:**
```
?prune    <page(s)>
?announce <text>
```
"""

@bot.event
async def on_command_error(error, ctx):
    embed = discord.Embed(color = discord.Color(0).gold())
    channel = ctx.message.channel
    footer = "Triggered by {}".format(ctx.message.author.name)
    if isinstance(error, commands.MissingRequiredArgument):
        embed.description = missingargu.format(ctx.message.author.mention)
        embed.set_footer(text=footer, icon_url="https://images.discordapp.net/avatars/431311040463110166/a4a4c55eb4d8ccf945e83f221dcf0b35.png")
        await ctx.bot.send_message(channel, embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed.description = missingargu.format(ctx.message.author.mention)
        embed.set_footer(text=footer, icon_url="https://images.discordapp.net/avatars/431311040463110166/a4a4c55eb4d8ccf945e83f221dcf0b35.png")
        await ctx.bot.send_message(channel, embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        embed.description = ":thinking: Command not found - ?help for command list"
        await ctx.bot.send_message(channel, embed=embed)
    elif isinstance(error, commands.CommandOnCooldown):
        embed.description = ":stuck_out_tongue_winking_eye: Command on cooldown - Please wait wait for {} seconds".format(30)
        await ctx.bot.send_message(channel, embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed.description = ':x: Missing "DJ" Role - Assign a "DJ" role to someone' + '\n'
        embed.description += '\n'
        embed.description += """:bulb: ?setdj - Incoming soon"""
        await ctx.bot.send_message(channel, embed=embed)

@bot.event
async def on_ready():
    embed = discord.Embed(color = discord.Color(0).gold())
    print ("System is ready")
    print ("I am running on " + bot.user.name)
    print ("With the ID: " + str(bot.user.id))
    print ("___________________________")
    await bot.change_presence(game=discord.Game(name='?help | {}'.format(len(bot.servers)) + ' servers'))
    embed.description = "Bot is now working"

class Commands:
    def __init__(self, bot):
        self.bot = bot 

#COGS
if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc ='{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

bot.run("bot token")
