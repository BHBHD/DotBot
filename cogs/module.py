import discord
from discord.ext import commands


class ModulesCog(commands.Cog, name='Module'):

    """Owner Only Command"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(hidden=True)
    @commands.is_owner()
    async def module(self, ctx):
        """ Module help command. """
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Module Commands", color=0x8f00ff,
                                  description="There are actually 3 Commands to use.\n "
                                              "All Commands in this Group are Bot-Owner only!\n\n"
                                              f"{ctx.prefix}module load <ModuleName> -> "
                                              "Loads a Module\n"
                                              f"{ctx.prefix}module unload <ModuleName> -> "
                                              "Unloads a Module\n"
                                              f"{ctx.prefix}module reload <ModuleName> -> "
                                              "Reloads a Module")
            await ctx.send(embed=embed)

    @module.command()
    async def load(self, ctx, *, cog: str):
        """ Load a Module. """
        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            embed = discord.Embed(description='**`ERROR:`** {} - {}'.format(type(e).__name__, e),
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f'\u2705 **`SUCCESS`**:', description=f'Addon "{str.title(cog)}" loaded',
                                  colour=0x8f00ff)
            await ctx.send(embed=embed)

    @module.command()
    async def unload(self, ctx, *, cog: str):
        """ Unload a Module. """
        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            embed = discord.Embed(description='**`ERROR:`** {} - {}'.format(type(e).__name__, e),
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f'\u2705 **`SUCCESS`**:', description=f'Addon "{str.title(cog)}" unloaded',
                                  colour=0x8f00ff)
            await ctx.send(embed=embed)

    @module.command()
    async def reload(self, ctx, *, cog: str):
        """ Reload a Module. """
        try:
            self.bot.unload_extension(f'cogs.{cog}')
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            embed = discord.Embed(description='**`ERROR:`** {} - {}'.format(type(e).__name__, e),
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f'\u2705 **`SUCCESS`**:', description=f'Addon "{str.title(cog)}" reloaded',
                                  colour=0x8f00ff)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ModulesCog(bot))