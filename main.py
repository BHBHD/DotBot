import keys
import discord
import asyncio
import sys
import sqlite3
import traceback
from discord.ext import commands


async def determine_prefix(bot, message):
    db = sqlite3.connect('database/guilds.db')
    cursor = db.cursor()
    cursor.execute(f'SELECT prefix FROM prefix WHERE guild_id = {message.guild.id}')
    result = cursor.fetchone()
    return commands.when_mentioned_or(result[0])(bot, message)

bot = commands.Bot(command_prefix=determine_prefix, case_insenitive=False)
bot.remove_command('help')

initial_extensions = ['cogs.help',
                      'cogs.module',
                      'cogs.events',
                      'cogs.commands',
                      'cogs.moderation']


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=1, name='Loading.'))
    if __name__ == '__main__':
        for extension in initial_extensions:
            try:
                bot.load_extension(extension)
                await bot.change_presence(activity=discord.Activity(type=1, name=f'Loading..'))
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f'Failed to load extension {extension}', file=sys.stderr)
                traceback.print_exc(e)
    print(f"{bot.user} loading finish!")
    return await bot.change_presence(activity=discord.Activity(type=1, name='DotBot'),
                                     status=discord.Status.dnd)

bot.run(keys.TOKEN)
