import discord
import os
import asyncio
from rcon.source import rcon
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks

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
    global server, chat
    server = bot.get_guild(server)
    chat = server.get_channel(chat)

async def servermsg(message: str):
    return await rcon('servermsg', f'"{message}"', host=os.getenv('RCON_HOST'), port=int(os.getenv('RCON_PORT')), passwd=os.getenv('RCON_PASSWORD'))

@tasks.loop(minutes=1)
async def restart_warning():
    now = datetime.now(timezone.utc)
    delta = now.hour // 6 + 1
    print('delta is', delta)
    next_restart = datetime(now.year, now.month, now.day, hour=6 * delta, tzinfo=timezone.utc)
    print(now.replace(microsecond=0))
    until = next_restart - now.replace(microsecond=0)
    times = [30, 10, 5, 1]
    print(until)
    for minutes in times:
        print(until.seconds, minutes * 60)
        if until.seconds == minutes * 60:
            await chat.send(f"**Server restart <t:{int(next_restart.timestamp())}:R>!**")
            await servermsg(f"The server will restart in {minutes} minute(s)!")
            break
    print('loop finished.  next restart:', next_restart)

def is_developer():
    async def predicate(ctx):
        devrole = ctx.guild.get_role(1033815896197709855)
        return devrole in ctx.author.roles
    return commands.check(predicate)



@bot.slash_command()
@is_developer()
async def server_message(ctx: discord.ApplicationContext, *, message: str):
    response = await servermsg(message)
    print(response)
    await ctx.respond(f'{response}', ephemeral=True)


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