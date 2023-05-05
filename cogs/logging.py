import discord
import os
import datetime
from discord.ext import commands, tasks

from dotenv import load_dotenv
load_dotenv(override=True)

logging_channel = 1104100574158405685
log_path = "/home/pzuser/Zomboid/server-console.txt"

lines = {}

class ServerConsole:
    lines = dict()
    index = 0

    @classmethod
    def update(cls):
        with open(log_path, 'r') as file:
            file.seek(cls.index)
            while True:
                line = file.readline()
                if line == '':
                    break
                else:
                    cls.add_line(line)
                    cls.index += 1

    @classmethod
    def add_line(cls, line: str):
        """Compiles and sorts log lines"""
        line = decode_line(line)
        if not cls.lines[line['id']]:
            #create a new line
            cls.lines[line['id']] = {
                'type' : line['type'],
                'category' : line['category'],
                'content' : line['content']
            }
        else:
            #join the lines together
            cls.lines[line['id']]['content'] += '\n' + line['content']
        cls.lines[line['id']]['timestamp'] = line['timestamp']


def decode_line(line):
    return dict(
        type = line.split(':')[0].strip(),
        category = line.split(':')[1].split(',')[0].strip(),
        timestamp = line.split(',')[1].strip().split('>')[0].strip(),
        id = line.split('>')[1].strip().replace(',', ''),
        content = line.split('>')[2]
    )

async def error_embed(dataline):
    embed = discord.Embed(
        title=dataline['category'],
        description=f"```\n{dataline['content']}\n```",
        color=discord.Color.brand_red())
    embed.timestamp = dataline['timestamp']
    return embed

async def general_embed(dataline):
    embed = discord.Embed(
        title=dataline['category'],
        description=dataline['content']
    )
    embed.timestamp = dataline['timestamp']
    return embed


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

