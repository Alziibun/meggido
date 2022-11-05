import tempfile
import discord
import os
import asyncio
import secrets
import string
import sqlite3
import database as db
from ftplib import FTP
from rcon.source import rcon
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.commands import SlashCommandGroup
from discord import option


load_dotenv(override=True)

server = None


def generate_password(pwd_length=8):
    alphabet = string.ascii_letters + string.digits
    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))
    return pwd

def credential_embed(username, password, author: discord.Member=None):
    embed = discord.Embed(title='Perdition Login Information', color=discord.Colour.brand_green())
    embed.add_field(name='IP Address', value=f'`{os.getenv("RCON_HOST")}`')
    embed.add_field(name="Port", value="`31700`")
    embed.add_field(name="Account: Username", value=username, inline=False)
    embed.add_field(name='Account: Password', value=password)
    embed.set_footer(text='TIP: Leave the "Server Password" field blank')
    if author is not None:
        embed.set_author(name=f"{author.display_name.split('|')[0].strip()} whitelisted you", icon_url=author.display_avatar.url)
    return embed

def application_embed(member: discord.Member, username: str=None, note: str=""):
    embed = discord.Embed(color=discord.Color.blurple())
    embed.set_author(name=member.name, icon_url=member.avatar.url)
    embed.add_field(name='Username', value=username if username is not None else member.name)
    if note:
        embed.add_field(name='Note', value=note, inline=False)
    return embed

async def adduser(username: str, password: str=generate_password()):
    response = await rcon('adduser', f'"{username}"', f'"{password}"',
                          host=os.getenv('RCON_HOST'),
                          port=int(os.getenv('RCON_PORT')),
                          passwd=os.getenv('RCON_PASSWORD')
                          )
    if 'exist' in response:
        raise IndexError(response)
    return username, password

async def kickuser(username: str, reason: str=''):
    pass

async def banuser(username: str, reason: str=''):
    pass

async def denizen(user: discord.Member, username: str):
    den = server.get_role(1029288892270129153)
    tour = server.get_role(1036008791105355907)
    await user.add_roles(den)
    await user.remove_roles(tour)
    await user.edit(nick=f"{username} | Denizen")


class Application(discord.ui.Modal):
    def __init__(self, member: discord.Member, *args, **kwargs):
        super().__init__(title="Whitelist Application", *args, **kwargs)
        self.add_item(discord.ui.InputText(label='Username', min_length=3, max_length=32, required=True, value=member.name))
        self.add_item(discord.ui.InputText(label='Note (optional)', style=discord.InputTextStyle.long, required=False))

    async def callback(self, interaction: discord.Interaction):
        name = self.children[0].value
        note = self.children[1].value
        print(note)
        chan = interaction.guild.get_channel(1037514532639215626)
        await chan.send(embed = application_embed(interaction.user, username=name, note=note), view = WLRequestControls(interaction.user))
        await interaction.response.send_message('Application sent successfully.', ephemeral=True)

class WLRequestControls(discord.ui.View):
    def __init__(self, member: discord.Member, *args, **kwargs):
        self.member = member
        print(member.name)
        super().__init__(timeout=None, *args, **kwargs)

    @discord.ui.button(label='Accept', custom_id='a1', style=discord.ButtonStyle.success)
    async def accept_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        print(self.member)
        try:
            user, pw = await adduser(self.member.name)
        except IndexError:
            return await interaction.response.send_message('You\'re already whitelisted!')
        dm = await self.member.create_dm()
        await interaction.message.delete()
        await dm.send(embed=credential_embed(user, pw, interaction.user))
        await interaction.response.send_message("Whitelist accepted.  Login credentials sent to user.", ephemeral=True)
        await denizen(self.member, user)
        await interaction.message.delete()

    @discord.ui.button(label='Deny', custom_id='d1', style=discord.ButtonStyle.red)
    async def deny_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Whitelist request denied", ephemeral=True)

async def can_dm_user(user: discord.User) -> bool:
    ch = user.dm_channel
    if ch is None:
        ch = await user.create_dm()
    try:
        await ch.send()
    except discord.Forbidden:
        return False
    except discord.HTTPException:
        return True

class WhitelistRequest(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
    @discord.ui.button(label="Request Whitelisting", custom_id='request')
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await can_dm_user(interaction.user):
            return await interaction.response.send_message("Please enable DMs with this server in order to send an application.  You will be DMed your login details when accepted.", ephemeral=True)
        db.fetch_serverdb()
        if db.find('whitelist', 'username', interaction.user.display_name.split('|')[0].strip()) is not None:
            return await interaction.response.send_message("You're already whitelisted", ephemeral=True)
        await interaction.response.send_modal(Application(interaction.user))

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    wl = SlashCommandGroup('whitelist', 'Manage server whitelist through RCON.')

    @wl.command(name='add')
    @option('user', description='The user to add to the whitelist.')
    @option('username', description='The username for the player.  Leave this empty to use the discord name')
    @option('password', description='Manually creates a password instead of having it generated automatically.')
    async def wl_adduser(self, ctx: discord.ApplicationContext, user: discord.Member, username: str=None, password: str=generate_password()):
        response = await adduser(username if username is not None else user.name, password)
        print(response)
        if 'exist' in response:
            await ctx.respond('That username already exists!', ephemeral=True)
        else:
            await ctx.respond(f"Username: `{username if username is not None else user.name}`\nPassword: `{password}`", ephemeral=True)

    @wl.command(name='remove')
    async def wl_remove(self, ctx: discord.ApplicationContext, username: str):
        response = await rcon('removeuserfromwhitelist', f'"{username}"',
                              host=os.getenv('RCON_HOST'),
                              port=int(os.getenv('RCON_PORT')),
                              passwd=os.getenv('RCON_PASSWORD')
                              )
        await ctx.defer()
        print(response)
        await ctx.send_followup(response, ephemeral=True)

    @wl.command(name='spawn')
    async def wl_spawn(self, ctx: discord.ApplicationContext):
        await ctx.respond(view=WhitelistRequest())

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(WhitelistRequest(), message_id=1037863899208368168)
        global server
        server = self.bot.get_guild(1029286298156011600)

def setup(bot):
    bot.add_cog(Whitelist(bot))


