import discord
import time
import asyncio
import random
import logging
from discord.ext.commands import Bot
from discord.ext import commands
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

class OtherCommands:
    """admin Commands of axo"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def prune(self, ctx, amount: int):
        """*prune messages"""
        embed = discord.Embed(color = discord.Color(0).gold())
        deleted = await self.bot.purge_from(ctx.message.channel, limit=amount)
        embed.description = "{} ".format(ctx.message.author.mention) + "has pruned {} message(s)".format(len(deleted))
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx, *args):
        """admin announcement"""
        embed = discord.Embed
        colors = {}
        if args:
            argstr = " ".join(args)
            if "-c " in argstr:
                text = argstr.split("-c ")[0]
                color_str = argstr.split("-c ")[1]
                color = colors[color_str]
            else:
                text = argstr
                color = discord.Color(0).red()
            await self.bot.delete_message(ctx.message)                
            await self.bot.say(embed=embed(color=color, description="**ADMIN:** " + text))
   
    @commands.command(pass_context=True)
    async def ping(self,ctx):
        """Show the bot's ping"""
        embed = discord.Embed(color = discord.Color(0).gold())
        channel = ctx.message.channel
        t1 = time.perf_counter()
        await self.bot.send_typing(channel)
        t2 = time.perf_counter()
        embed.description = ":ping_pong: {}ms".format(round((t2-t1)*1000))
        await self.bot.say(embed=embed)

        
def setup(bot):
    bot.add_cog(OtherCommands(bot))
    print("Commands Ready")
