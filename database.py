import cmath
import tempfile
import discord
import os
import sqlite3
from bs4 import dammit
from io import BytesIO, BufferedWriter
from ftplib import FTP
from rcon.source import rcon
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.commands import SlashCommandGroup
from discord import option
import chardet

load_dotenv(override=True)
archive = dict()
con = None
cur = None

con = sqlite3.connect('database.sqlite3')
cur = con.cursor()
print('Database connected.')

def pragma(table):
    return

def fetch_serverdb():
    print('Fetching server.db')
    with FTP() as ftp:
        ftp.connect(host= os.getenv('FTP_HOST'), port=int(os.getenv('FTP_PORT')))
        ftp.login(user=os.getenv('FTP_USER'), passwd=os.getenv('FTP_PASSWORD'))
        print('Connected to FTP.')
        ftp.cwd('db')
        with tempfile.TemporaryDirectory() as path:
            with open(os.path.join(path, 'servertest.db'), 'wb+') as buffer:
                print('Attempting to create temp db...')
                resp = ftp.retrbinary("RETR servertest.db", buffer.write)
                print(resp)
                buffer.seek(0)
                encoding_prediction = chardet.detect(buffer.read())
                encoded = buffer.read().decode(encoding_prediction['encoding'], errors='replace')
                print(encoded)
                tempdb = sqlite3.connect(os.path.join(path, 'servertest.db'))
                tempdb.executescript(encoded)
                print('Successfully connected to in-memory db.')
                c = tempdb.cursor()
                c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                global archive
                for table in c.fetchall():
                    table = table[0]
                    if table not in ('sqlite_sequence'):
                        pragma = tempdb.execute(f"PRAGMA table_info('{table}')").fetchall()
                        build = {}
                        for col in pragma:
                            col_name = col[1]
                            column = []
                            for value in c.execute(f'SELECT {col_name} FROM {table}').fetchall():
                                if value is not None:
                                    column.append(value[0])
                                else:
                                    column.append(value)
                            build.update({col_name : column})
                        archive.update({table : build})
                        print(table, 'archived.')
                tempdb.close()
                print('Archive updated with most recent server.db entries.')

def select(table, index):
    return {column : archive[table][column][index] for column in archive[table]}

def find(table, column, value):
    if value in archive[table][column]:
        return select(table, archive[table][column].index(value))
    return None


def commit(*query):
    for q in query:
        cur.execute(q)
    con.commit()

def add_user(member: discord.Member, zomboid: int, password: str=None):
    print(member, zomboid, password)
    query = """
    INSERT INTO user
        (discord_id, zomboid_id, password)
    VALUES
        (?, ?, ?)
    """
    try:
        con.execute(query, (member.id, zomboid, password))
        con.commit()
        print(f'Added {member.display_name} to the database.')
    except Exception as e:
        print('Failed to add user\nError:', e)

def predict_link(guild: discord.Guild):
    fetch_serverdb()
    members = [(member.display_name.split('|')[0].strip(), member) for member in guild.members if not member.bot]
    for name, member in members:
        data = find('whitelist', 'username', name) if find('whitelist', 'username', name) != None else find('whitelist', 'displayName', name)
        if data != None:
            print(data['id'])
            add_user(member, data['id'])
            print(name, 'linked to zomboid id:', data['id'])


# INIT

