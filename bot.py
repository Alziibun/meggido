import discord
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv(override=True)
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = discord.Bot(intents=intents, debug_guilds=[1029286298156011600])

chat = 1033897721721008128
server = 1029286298156011600
@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    global server, chat
    server = bot.get_guild(server)
    chat = server.get_channel(chat)

@tasks.loop(minutes=1)
async def restart_warning():
    now = datetime.utcnow()
    delta = now.hour // 6 + 1
    next_restart = datetime(now.year, now.month, now.day, hour=6 * delta)
    print(now.replace(microsecond=0))
    until = next_restart - now.replace(microsecond=0)
    times = [50, 45, 40, 35, 30, 10, 5, 1]
    print(until)
    for minutes in times:
        print(until.seconds, minutes * 60)
        if until.seconds == minutes * 60:
            await chat.send(f"The server restarts <t:{int(next_restart.timestamp())}:R>.")
            break
    print('loop finished.  next restart:', next_restart)

@restart_warning.before_loop
async def before_warning():
    await bot.wait_until_ready()
    now = datetime.utcnow()
    future = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    until = future - now.replace(microsecond=0)
    print('Sleeping for', until.total_seconds(), 'seconds')
    await asyncio.sleep(until.total_seconds())


restart_warning.start()

if __name__ == "__main__":
    # dir = os.path.dirname(__file__)
    # cogs = os.path.join(dir,'/cogs')
    # for ex in os.listdir(cogs):
    #     try:
    #         bot.load_extension(ex)
    #         print(ex, 'loaded.')
    #     except Exception as e:
    #         exc = "{}: {}".format(type(e).__name__, e)
    #         print('Failed to load extension {}\n{}'.format(ex, exc))
    bot.run(os.getenv("BOT_TOKEN"))