import discord
import sqlite3
import typing
import argparse, shlex
from .utils import checks
from discord.ext import commands
from .utils.formats import plural


def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class MemberNotFound(Exception):
    pass


async def resolve_member(guild, member_id):
    member = guild.get_member(member_id)
    if member is None:
        if guild.chunked:
            raise MemberNotFound()
        try:
            member = await guild.fetch_member(member_id)
        except discord.NotFound:
            raise MemberNotFound() from None
    return member


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                member_id = int(argument, base=10)
                m = await resolve_member(ctx.guild, member_id)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        if not can_execute_action(ctx, ctx.author, m):
            raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
        return m


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'`{ctx.author} (ID: {ctx.author.id}): {argument}\n`'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret


def safe_reason_append(base, to_append):
    appended = base + f'({to_append})'
    if len(appended) > 512:
        return base
    return appended


class ModerationCog(commands.Cog, name='Moderation'):

    """ Moderation Commands """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """ Bans a member from the server. """

        if reason is None:
            reason = f'`Action done by {ctx.author} (ID: {ctx.author.id})`'

        await ctx.guild.ban(member, reason=reason)

    @commands.command(aliases=['mban'])
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def multiban(self, ctx, members: commands.Greedy[MemberID], *, reason: ActionReason = None):
        """ Bans multiple members from the server. """

        if reason is None:
            reason = f'`Action done by {ctx.author} (ID: {ctx.author.id})`'

        total_members = len(members)
        if total_members == 0:
            return await ctx.send('Missing members to ban.')

        confirm = await ctx.prompt(f'This will ban **{plural(total_members):member}**. Are you sure?', reacquire=False)
        if not confirm:
            return await ctx.send('Aborting.')

        failed = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                failed += 1

        await ctx.send(f'Banned {total_members - failed}/{total_members} members.')

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(kick_members=True)
    async def softban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """ Soft bans a member from the server. """

        if reason is None:
            reason = f'`Action done by {ctx.author} (ID: {ctx.author.id})`'

        await ctx.guild.ban(member, reason=reason)
        await ctx.guild.unban(member, reason=reason)
        await ctx.send(f'{member} Soft Banned!.')

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason: ActionReason = None):
        """ Unbans a member from the server. """

        if reason is None:
            reason = f'`Action done by {ctx.author} (ID: {ctx.author.id})`'

        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}), previously banned for: {member.reason}.')
        else:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}).')

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """ Mutes given member. """
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        if reason is None:
            reason = f'`Action done by {ctx.author} (ID: {ctx.author.id})`'

        if not role:
            try:
                muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted, send_messages=False,
                                                  read_message_history=False,
                                                  read_messages=False)
            except discord.Forbidden:
                return await ctx.send("I have no permissions to make a muted role")
            await member.add_roles(muted)
            await ctx.send(f"{member.mention} muted for `{reason}`")
        else:
            await member.add_roles(role)
            await ctx.send(f"{member.mention} muted for `{reason}`")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(manage_permission=True)
    async def report(self, ctx, member: MemberID, *, reportReason: ActionReason):
        """ Reports given member """
        db = sqlite3.connect('database/reports.db')
        name = f'`{ctx.guild.id}`'
        cursor = db.cursor()
        found = False
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {name}(
            user_id INT,
            reason_msg TEXT,
            staff_id INT
        )
        ''')
        cursor.execute(f'SELECT user_id FROM {name}')
        users = cursor.fetchall()
        for user in users:
            if int(user[0]) == member.id:
                cursor.execute(f'UPDATE {name} SET reason_msg = {reportReason}, staff_id = {ctx.author.id} '
                               f'WHERE user_id = {member.id}')
                await ctx.send(f'{member} is reported!')
                found = True
        if found is False:
            sql = f"INSERT INTO {name}(user_id, reason_msg, staff_id) VALUES(?, ?, ?)"
            val = (member.id, reportReason, ctx.author.id)
            cursor.execute(sql, val)
            await ctx.send(f'{member} is reported!')
        cursor.close()
        db.commit()
        db.close()

    @commands.command(aliases=['clear', 'cl'])
    @commands.guild_only()
    @checks.has_permissions(manage_message=True)
    async def clean(self, ctx, count: int, member: typing.Optional[discord.Member] = None,
                    *, flag: typing.Optional[str] = None):
        parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        parser.add_argument('-ma')

        try:
            args = parser.parse_args(shlex.split(flag))
        except Exception as e:
            return await ctx.send(str(e))

        if args.ma:
            print(args.ma)


def setup(bot):
    bot.add_cog(ModerationCog(bot))
