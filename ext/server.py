import discord
import asyncio
import os, sys
from typing import List
import subprocess

session_name = 'zomboid'

async def until_quit():
    output = "server"
    while "server" in output:
        result = subprocess.run(['tmux', 'list-windows'], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        print(output)
        await asyncio.sleep(1)
    else:
        print("Window closed")

def command(*args):
    os.system(f"tmux send -t {session_name}:1 {' SPACE '.join(args)} ENTER")

def message(msg):
    command("servermsg", f'"{msg}"')

def quit():
    command('quit')

def start():
    os.system(f'tmux new-window -t {session_name}:1 -n server "bash /opt/pzserver/start-server.sh"')

async def restart():
    quit()
    await until_quit()
    await asyncio.sleep(5)
    start()