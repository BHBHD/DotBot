import keys
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='?')

@bot.event
async def on_ready():
    print(f"Online as {bot.user}")
    return await bot.change_presence(activity=discord.Activity(type=1, name='DotBot'), status=discord.Status.dnd)

@bot.command()
async def ping(ctx):
    ms = round(bot.latency, 1) * 1000
    await ctx.send(f'Pong! `{int(ms)}ms`')

bot.run(keys.Token)
