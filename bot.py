import discord
import os
import asyncio
import pytz
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
    global server, chat
    server = bot.get_guild(server)
    chat = server.get_channel(chat)
    restart_warning.start()

@bot.event
async def on_member_join(member: discord.Member):
    tourist = server.get_role(1036008791105355907)
    await member.add_roles(tourist)

async def servermsg(message: str):
    return await rcon('servermsg', f'"{message}"', host=os.getenv('RCON_HOST'), port=int(os.getenv('RCON_PORT')), passwd=os.getenv('RCON_PASSWORD'))
async def worldsave():
    return await rcon('save', host=os.getenv('RCON_HOST'), port=os.getenv('RCON_PORT'), passwd=os.getenv('RCON_PASSWORD'))

@bot.slash_command()
async def when_restart(ctx):
    when, until = get_restart()
    await ctx.respond(f"**Server restart <t:{int(when.timestamp())}:R>!**")

def get_restart():
    server_tz = pytz.timezone('Europe/London')
    utc_time = pytz.utc.localize(datetime.utcnow())
    now = server_tz.normalize(utc_time.astimezone(server_tz))
    dst = int(now.astimezone(server_tz).dst() != timedelta(0))
    delta = (now.hour - int(not dst)) // 6

    print('delta is', delta)
    next_restart = server_tz.normalize(datetime(now.year, now.month, now.day, hour=1 - dst, tzinfo=now.tzinfo))
    print(6 * delta + 7 - dst, "hours")
    if now.hour >= 1:
        print(timedelta(hours=6 * delta + 6 + dst))
        next_restart += timedelta(hours=6 * delta + 6 + dst)
    return next_restart, next_restart - now.replace(second=0, microsecond=0)

@tasks.loop(minutes=1)
async def restart_warning():
    await create_listing()
    when, until = get_restart()
    times = [30, 15, 10, 5, 3, 1]
    print('Time until restart', until)
    if until.seconds == times[0] * 60:
        await chat.send(f"**Server restart <t:{int(when.timestamp())}:R>!**")
    for minutes in times:
        if until.seconds == minutes * 60:
            await Server.message(f"The server will restart in {minutes} minute(s)!")
            break
    print('loop finished.  next restart:', when)

srv = bot.create_group('server', 'Administrative RCON commands to communicate to the server.')

@srv.command(name='message', description='Sends a server message to the server.')
async def server_message(ctx: discord.ApplicationContext, *, message: str):
    await Server.message(message)
    await ctx.respond(f'sent', ephemeral=True)

@srv.command(name='save', description='Commands the server to save the world.')
async def server_save(ctx: discord.ApplicationContext):
    response = await worldsave()
    print(response)
    await ctx.respond(f"{response}", ephemeral=False)

@srv.command(name='reload', description='Reloads the server options.  This allows you to change settings without requiring a restart')
async def server_reloadoptions(ctx: discord.ApplicationContext):
    response = await rcon('reloadoptions', host=os.getenv('RCON_HOST'), port=int(os.getenv('RCON_PORT')), passwd=os.getenv('RCON_PASSWORD'))
    print(response)
    await ctx.respond(f"{response}")

@srv.command(name='shutdown')
async def server_shutdown(ctx: discord.ApplicationContext):
    response = await rcon('quit', host=os.getenv('RCON_HOST'), port=int(os.getenv('RCON_PORT')), passwd=os.getenv('RCON_PASSWORD'))
    print(response)
    await ctx.respond(f"{response}")


@restart_warning.before_loop
async def before_warning():
    await bot.wait_until_ready()
    chan: discord.TextChannel = server.get_channel(1036141105697271858)
    await chan.purge()
    now = datetime.utcnow()
    future = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    until = future - now.replace(second=0, microsecond=0)
    print('Sleeping for', until.total_seconds(), 'seconds')
    await asyncio.sleep(until.total_seconds())

options = []
def rcon_get_options():
    with Client(os.getenv('RCON_HOST'), int(os.getenv('RCON_PORT')), passwd=os.getenv('RCON_PASSWORD')) as client:
        response = client.run('showoptions')
        return [row[2:].split('=') for row in [i for i in response.split('\n')]][1:]

def serveroptions(ctx: discord.AutocompleteContext):
    global options
    if not options:
        options = rcon_get_options()
    print([value[0] for value in options if ctx.value.lower() in value[0].lower()])
    return [value[0] for value in options if ctx.value.lower() in value[0].lower()]

@bot.slash_command()
@option('option', parameter_name='opt', autocomplete=serveroptions)
async def show_option(ctx: discord.ApplicationContext, opt: str):
    options = {value[0] : value[1] for value in rcon_get_options()}
    if opt in options.keys():
        await ctx.respond(f"`{options[opt]}`")

@bot.slash_command()
async def linkmembers(ctx):
    db.predict_link(ctx.guild)
    await ctx.respond('Check console.', ephemeral=True)

@bot.slash_command(name='commit')
async def commit_to_db(ctx, *, query):
    try:
        query = query.strip('` ')
        query = query.replace('sql', '')
        db.commit(query)
        await ctx.respond('Commit successful.')
    except Exception as e:
        await ctx.respond(f'Commit failed.\nError: {e}')

async def get_players():
    response = await rcon('players', host=os.getenv('RCON_HOST'), port=int(os.getenv('RCON_PORT')),passwd=os.getenv('RCON_PASSWORD'))
    lines = response.splitlines()
    names = [name[1:] for name in lines[1:]]
    players = []
    for member in server.members:
        name = member.display_name.split('|')[0].strip()
        if name.lower() in [lname.lower() for lname in names]:
            players.append((name, member))
    return players

async def online_embed(member: discord.Member):
    embed = discord.Embed(color=member.top_role.color)
    embed.set_author(name=member.display_name.split('|')[0].strip(), icon_url=member.display_avatar)
    return embed

listing = {}
async def create_listing():
    chan: discord.TextChannel = server.get_channel(1036141105697271858)
    try:
        players = await get_players()
    except Exception as e:
        print("Couldn't get players\n",e)
        return
    print([name for name, member in players])
    print(list(listing.keys()))
    if [name for name, member in players] != list(listing.keys()):
        woosh = list(listing.items())
        for name, msg in woosh:
            print(name)
            if name not in [name for name, member in players]:
                await msg.delete()
                del listing[name]
    for name, member in players:
        if name not in listing.keys():
            msg = await chan.send(embed=await online_embed(member))
            listing.update({name : msg})
replay = bot.create_group('replay', 'Record/Play a recording of player activity.')

@bot.slash_command()
async def players(ctx):
    await create_listing()
    await ctx.respond('test')

if __name__ == "__main__":
    for ex in os.listdir(os.getcwd() + '\\cogs'):
        try:
            ex = ex.split('.')[0]
            bot.load_extension(f"cogs.{ex}")
            print(ex, 'loaded.')
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(ex, exc))
    bot.run(os.getenv("BOT_TOKEN"))