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

def command(cmd, args):
    os.system(f"tmux send -t {session_name}:1 {cmd} {args} ENTER")

def send(*args):
    command("stuff", f"{' '.join(args)}")

def message(msg):
    send("servermsg", f'"{msg}"')

def quit():
    send('quit')

def start():
    subprocess.run(['tmux', 'new-window', '-t', f'{session_name}:1', '-n', 'server', '"bash /opt/pzserver/start-server.sh"'])

async def restart():
    quit()
    await until_quit()
    start()