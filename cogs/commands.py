import time
import pytz
import typing
import discord
import sqlite3
import datetime
from datetime import date
from discord.ext import commands
from collections import Counter


def calculate_age(change_date):
    today = date.today()
    years = today.year - change_date.year
    months = today.month - change_date.month
    days = today.day - change_date.day
    return f"{years} years {months} months and {days} days"


class MemberRoles(commands.MemberConverter):
    async def convert(self, ctx, argument):
        member = await super().convert(ctx, argument)
        return [role.name for role in member.roles[1:]]


class GeneralCog(commands.Cog, name='General Commands'):
    """General Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['latency', 'delay'])
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        message = await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong!  `{int(ping)}ms`")

    @commands.command(name='bot', aliases=['info', 'botinfo'])
    async def _bot(self, ctx):
        """ Bot Info """
        embed = discord.Embed(title='Bot Information', description='Created by ɃĦɃĦĐ#2224', color=0x8f00ff)

        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/669205528404295722/'
                                '5d1ecffd4989f2bb61cfb26a4d0417ea.png?size=256')
        embed.set_footer(text=f'{self.bot.user.name}',
                         icon_url='https://cdn.discordapp.com/avatars/669205528404295722/'
                                  '5d1ecffd4989f2bb61cfb26a4d0417ea.png?size=256')
        embed.add_field(name='**Total Guilds**', value=f'`{len(list(self.bot.guilds))}`', inline=True)
        embed.add_field(name='**Total Users**', value=f'`{len(list(self.bot.users))}`', inline=True)
        channel_types = Counter(isinstance(c, discord.TextChannel) for c in self.bot.get_all_channels())
        text = channel_types[True]
        embed.add_field(name='**Total Channels**', value=f'`{text}`', inline=True)
        embed.add_field(name='**Python Version**', value='`3.7`', inline=True)
        embed.add_field(name='**Discord.py Version**', value='`1.2.5`', inline=True)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        """ Bot Invite Link """
        embed = discord.Embed(title='Invite Me!',
                              color=0x8f00ff)
        embed.add_field(name='Link:', value='[Click Here](https://discordapp.com/api/oauth2/authorize?'
                                            'client_id=669205528404295722&permissions=8&scope=bot)')
        embed.set_footer(text=f'{self.bot.user.name}',
                         icon_url='https://cdn.discordapp.com/avatars/669205528404295722/'
                                  '5d1ecffd4989f2bb61cfb26a4d0417ea.png?size=256')
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    # ADD HELP COMMAND USING SOME COG FEATURE?


class ToolsCog(commands.Cog, name='Tools Commands'):
    """Tools & Utilities Commands"""

    def __init__(self, bot):
            self.bot = bot

    # Tools & Utilities
    @commands.command()
    async def prefix(self, ctx, *, guild_id=None):
        """ Shows the command prefix on current server or specified server. """
        if guild_id is None:
            db = sqlite3.connect('database/guilds.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT prefix FROM prefix WHERE guild_id = {ctx.guild.id}')
            prefix = cursor.fetchone()
            if prefix is not None:
                await ctx.send(f'Prefix of `{ctx.guild}`: `{prefix[0]}`')
            else:
                await ctx.send(f'Prefix of `{ctx.guild}`: `{prefix[0]}`')
            cursor.close()
            db.close()
        elif guild_id is not None:
            db = sqlite3.connect('database/guilds.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT prefix FROM prefix WHERE guild_id = {int(guild_id)}')
            prefix = cursor.fetchone()
            if prefix is None:
                await ctx.send(f'Prefix of `{str(guild_id)}`: `{prefix}`')
            else:
                await ctx.send(f'Prefix of `{str(guild_id)}`: `{prefix}`')
            cursor.close()
            db.close()

    @commands.command(aliases=['c', 'calc', 'math'])
    async def calculate(self, ctx, *, operation=None):
        """ Calculator. Example: 2+2 """
        try:
            operation = eval(operation)
        except ZeroDivisionError:
            await ctx.send('`Error:` division by zero!')
            return
        except Exception as e:
            print(e)
            await ctx.send('`Error:` expression could not be calculated!')
            return
        await ctx.send(f'Result: {operation}')

    @commands.command(aliases=['ctime', 'gettime'])
    async def currenttime(self, ctx, *, timezone=None):
        """ Shows UTC time, or the timezone you chose. """
        if timezone is None:
            utc_now = pytz.utc.localize(datetime.datetime.utcnow())
            # Wed Jan 29 15:34:43 (UTC +05:30)
            current_time = utc_now.strftime("%a %b %d %H:%M:%S (%Z %z)")
            await ctx.send(current_time)
        elif timezone is not None:
            try:
                utc_now = pytz.utc.localize(datetime.datetime.utcnow())
                pst_now = utc_now.astimezone(pytz.timezone(timezone))
                current_time = pst_now.strftime("%a %b %d %H:%M:%S (%Z %z)")
                await ctx.send(current_time)
            except pytz.exceptions.UnknownTimeZoneError:
                await ctx.send(f'`Unknown TimeZone:` {timezone}')

    @commands.command()
    async def listroles(self, ctx):
        """ List roles and their IDs, and some other stuff on the server. """
        role_list = ""
        global main_name
        roles = ctx.guild.roles
        for role in roles:
            role_name = str(role)
            if len(role_name) <= 26:
                space = 26 - len(role_name)
                role_with_space = len(role_name)+space
                main_name = role_name.ljust(role_with_space)
            role_list += f"`{main_name}: {role.id} {role.colour} " \
                         f"ME: {role.permissions.mention_everyone}`\n"
        await ctx.send('(ME = mention everyone perms)\n' + role_list)

    # COMPLETE POLL COMMAND
    @commands.command()
    async def poll(self, ctx, question, opn1, opn2, opn3=None, opn4=None, opn5=None, opn6=None):
        """ Creates a reaction poll. """
        ans = f":one: {opn1}\n" \
              f":two: {opn2}\n"
        count = 0
        while count == 3:
            pass
        embed = discord.Embed(title=f'{question}')
        embed.set_author(name=f'{ctx.author}', icon_url=f'{ctx.author.avatar_url}')
        await ctx.send(embed=embed)

    # ERROR FOR POLL COMMAND
    @poll.error
    async def poll_error(self, ctx, error):
        await ctx.send('```Poll <Topic:Text - Description of the poll> <Option1:Text> <Option2:Text> '
                       '[Option3:Text] [Option4:Text] [Option5:Text] [Option6:Text]``` '
                       'Invalid arguments provided: Not enough arguments passed')

    # COMPLETE UNDELETE COMMAND
    @commands.command(aliases=['ud'])
    async def undelete(self, ctx, arg=None):
        """ Views your recent deleted messages, or all users deleted messages in this channel. """
        pass

    # COMPLETE VIEWPERMS COMMAND
    @commands.command()
    async def viewperms(self, ctx, target: typing.Union[discord.Member, discord.Role]):
        """ Shows you requested user's permissions in this channel. """
        try:
            allowed_commands = ""
            permissions = target.permissions_in(ctx.channel)
            for perm in permissions:
                allowed_commands += ' `' + perm[0] + '` '
            await ctx.send(allowed_commands)
        except Exception as e:
            print(e)
            await ctx.send(':(')

    # COMPLETE STATS COMMAND
    @commands.command(aliases=['serverinfo'])
    async def stats(self, ctx):
        """ Shows server stats (only if public stats are enabled). """
        roles_list = ""
        guild = self.bot.get_guild(ctx.guild.id)
        roles = guild.roles
        for role in roles:
            roles_list += str(role) + ', '

        embed = discord.Embed(title='Server Stats')
        embed.set_author(name=f'{guild.name}', icon_url=f'{guild.icon_url}')
        embed.set_footer(text=f'ID: {guild.id} | Server Created ')
        embed.timestamp = guild.created_at
        # embed.add_field(name='Members Joined 24h', value=f'')
        # embed.add_field(name='Members Left 24h', value=f'')
        # embed.add_field(name='Members Messages 24h', value=f'')
        embed.add_field(name='Server Owner', value=f'{guild.owner}')
        embed.add_field(name='Region', value=f'{guild.region}')
        embed.add_field(name='Channel Categories', value=f'{len(list(guild.categories))}')
        embed.add_field(name='Text Channels', value=f'{len(list(guild.text_channels))}')
        embed.add_field(name='Voice Channels', value=f'{len(list(guild.voice_channels))}')
        embed.add_field(name='Total Members', value=f'{len(list(guild.members))}')
        # embed.add_field(name='Members Online', value=f'{}')
        embed.add_field(name='Role List', value=f'{roles_list}')
        await ctx.send(embed=embed)

    # ADD CUSTOM COMMANDS

    @commands.command(aliases=['whoami'])
    async def whois(self, ctx, user: discord.User):
        """ Shows information about given member. """
        guild = self.bot.get_guild(ctx.guild.id)
        member = guild.get_member(user.id)
        embed = discord.Embed(title=f'{user.name}')
        embed.set_thumbnail(url=f'{user.avatar_url}')
        embed.add_field(name='ID', value=f'{user.id}')
        embed.add_field(name='Avatar', value=f'[Click Here]({user.avatar_url})')
        embed.add_field(name='Account Created', value=f'{user.created_at}')
        embed.add_field(name='Account Age', value=f'{calculate_age(user.created_at)}')
        embed.add_field(name='Joined Server At', value=f'{member.joined_at}')
        embed.add_field(name='Joined Server Age', value=f'{calculate_age(member.joined_at)}')
        await ctx.send(embed=embed)

    @commands.command()
    async def role(self, ctx, *, member: MemberRoles = None):
        """ Give yourself a role of a given member. """
        await ctx.send('I see the following roles: ' + ', '.join(member))


def setup(bot):
    bot.add_cog(GeneralCog(bot))
    bot.add_cog(ToolsCog(bot))
