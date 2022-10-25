import tempfile
import discord
import os
import asyncio
import secrets
import string
import sqlite3
from ftplib import FTP
from rcon.source import rcon
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.commands import SlashCommandGroup
from discord import option

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def adduser(self, username: str, password: str):
        pass

    async def kickuser(self, username: str, reason: str=''):
        pass

    async def banuser(self, username: str, reason: str=''):
        pass

    @staticmethod
    def generate_password(pwd_length = 8):
        alphabet = string.ascii_letters + string.digits
        pwd = ''
        for i in range(pwd_length):
            pwd += ''.join(secrets.choice(alphabet))
        return pwd

    wl = SlashCommandGroup('whitelist', 'Manage server whitelist through RCON.')

    @wl.command(name='add')
    @option('user', description='The user to add to the whitelist.')
    @option('username', description='The username for the player.  Leave this empty to use the discord name')
    @option('password', description='Manually creates a password instead of having it generated automatically.')
    async def wl_adduser(self, ctx: discord.ApplicationContext, user: discord.Member, username: str=None, password: str=generate_password()):

        response = await rcon('adduser', f'"{username if username is not None else user.name}"', f'"{password}"',
                              host=os.getenv('RCON_HOST'),
                              port=int(os.getenv('RCON_PORT')),
                              passwd=os.getenv('RCON_PASSWORD')
                              )
        await ctx.defer()
        print(response)
        await ctx.send_followup(response, ephemeral=True)

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

def setup(bot):
    bot.add_cog(Whitelist(bot))


