import discord
import sqlite3
from discord.ext import commands


class EventsCog(commands.Cog, name='Events'):

    """Handle All Events"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """ Server Join Event """
        db = sqlite3.connect('database/guilds.db')
        cursor = db.cursor()

        # Sets the Bot Prefix
        cursor.execute(f'INSERT INTO prefix(guild_id, prefix) VALUES({guild.id}, "-")')

        # Close all the open methods
        cursor.close()
        db.commit()
        db.close()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """ Server Join Event """
        db = sqlite3.connect('database/guilds.db')
        cursor = db.cursor()

        # Sets the Bot Prefix
        cursor.execute(f'DELETE FROM prefix WHERE guild_id = {guild.id}')

        # Close all the open methods
        cursor.close()
        db.commit()
        db.close()


def setup(bot):
    bot.add_cog(EventsCog(bot))
