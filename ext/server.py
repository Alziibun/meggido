import discord
import asyncio
import os, sys
from typing import List
import subprocess

session_name = 'pz'

def get_active_screens() -> List[str]:
    result = subprocess.run(['screen', '-ls'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    if "No sockets found" in output:
        return []
    assert "There is a screen on" in output

    lines = []
    for line in output.splitlines():
        if line.startswith('\t'):
            lines.append(line)

    session_names = []
    for line in lines:
        line = line.strip()
        line = line.split('\t')[0]
        line = line.split('.')[1]
        session_names.append(line)
    return session_names

async def until_quit():
    output = "server"
    while "server" in output:
        result = subprocess.run(['tmux', 'list-windows'], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        print(output)
        await asyncio.sleep(1)
    else:
        print("Window closed")

def start_screen():
    subprocess.run(['screen', '-d', '-m', '-S', session_name])

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