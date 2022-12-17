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

def start_screen():
    subprocess.run(['screen', '-d', '-m', '-S', session_name])

def command(cmd, args):
    subprocess.run(['screen', '-S', session_name, '-p 0', '-X', cmd, args])

def send(*args):
    command("stuff", f"\'{' '.join(args)}\'^M")

def message(msg):
    send("servermsg", f'"{msg}"')

def quit_server():
    send('quit')

def start_server():
    command("bash", "/opt/pzserver/start-server.sh")

def restart_server():
    quit_server()
    start_server()