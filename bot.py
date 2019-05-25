import discord
from discord.ext import commands

description = '''A bot to have a nice tool for planing pnp parties in discord.'''

token = "strenggeheimespasswort"
id = "581815713589755904"

bot = commands.Bot(command_prefix='!', description=description)


@bot.event
async def on_ready():
    print('Logged in as {} with ID {}'.format(bot.user.name, bot.user.id))
    print('------')


@bot.command()
async def player(ctx, text:str):
    await ctx.send(text)

@bot.command()
async def gm(ctx, date:str ="today", ):
    if date:
        await ctx.send(date)


@bot.command()
async def help(ctx, command:str = None):
    pass

@bot.command()
async def help(ctx, command:str = None):
    pass


bot.run(token)
