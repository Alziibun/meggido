import discord
import os
import asyncio
import pytz
from ext.perdition import Perdition
from ext.server import Server
import database as db
from discord import option
from rcon.source import rcon, Client
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.commands import SlashCommandGroup

load_dotenv(override=True)
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = discord.Bot(intents=intents, debug_guilds=[1029286298156011600])

chat = 1029293109567307856
server = 1029286298156011600
@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    print('Starting Project Zomboid server')
    await Server.start()
    print('Server started')
    await Perdition.init(bot)

@bot.event
async def on_member_join(member: discord.Member):
    tourist = Perdition.server.get_role(1036008791105355907)
    await member.add_roles(tourist)

ext = bot.create_group("extension", "Bot command extension manager")

@ext.command(name='load')
async def load(ctx, extension):
    try:
        bot.load_extension(f"cogs.{extension}")
        await ctx.respond(f"{extension} loaded successfully.")
    except Exception as e:
        await ctx.respond(e)

@ext.command(name='unload')
async def unload(ctx, extension):
    try:
       bot.unload_extension(f"cogs.{extension}")
       await ctx.respond(f"{extension} unloaded successfully.")
    except Exception as e:
        await ctx.respond(e)

@ext.command(name='reload')
async def unload(ctx, extension):
    try:
       bot.unload_extension(f"cogs.{extension}")
       await asyncio.sleep(1)
       bot.load_extension(f"cogs.{extension}")
       await ctx.respond(f"{extension} reloaded successfully.")
    except Exception as e:
        await ctx.respond(e)

@bot.slash_command(name='commit')
async def commit_to_db(ctx, *, query):
    try:
        query = query.strip('` ')
        query = query.replace('sql', '')
        db.commit(query)
        await ctx.respond('Commit successful.')
    except Exception as e:
        await ctx.respond(f'Commit failed.\nError: {e}')

if __name__ == "__main__":
    for ex in os.listdir(os.getcwd() + '/cogs'):
        try:
            ex = ex.split('.')[0]
            bot.load_extension(f"cogs.{ex}")
            print(ex, 'loaded.')
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(ex, exc))
    bot.run(os.getenv("BOT_TOKEN"))