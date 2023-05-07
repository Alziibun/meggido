import re

import discord
import os
import datetime
from discord.ext import commands, tasks

from dotenv import load_dotenv
load_dotenv(override=True)
console_path = "/home/pzuser/Zomboid/server-console.txt"
log_channel_id = 1104100574158405685

class ServerConsole:
    def __init__(self):
        self.cursor = 0
        self.startup = True
        self.mods = {}
        self.permissions = {
            "read" : None,
            "write" : None
        }
        self.PZVersion = None
        self.servername = None
        self.port = None

    async def read(self, status, mod_status_callback):
        searches = {
            "Zomboid Version": r'(?<=version=)[0-9.]+',
            "Server Language": r'(?<=language is )[A-Z][A-Z]',
            "SteamAPI Status": r'(?<=Steam API initialised )\w+',
            "Public IP":       r'(?<=Public IP:)[0-9.]+',
        }
        with open(console_path) as file:
            file.seek(self.cursor)
            while (line := file.readline()) != '':
                if line.startswith("WARN"): continue #skip this
                if "Loading: /home/pzuser/Zomboid/Server/servertest_SandboxVars.lua" in line:
                    status("Loading Sandbox Variables")
                    continue
                if "Loading world..." in line:
                    status("Loading world...")
                    continue
                if "No valid token provided AND missing email or password. Connecting not possible!" in line:
                    status("Could not use Discord integration")
                if "Workshop: GetItemState()" in line:
                    mod_status = re.search(r'(?<=GetItemState\(\)=)\w+', line).group(0)
                    mod_id = re.search(r'(?<=ID=)[0-9]+', line).group(0)
                    mod_status_callback(mod_status, mod_id)

                for name, search in searches:
                    yield






    def findServerName(self, line):
        if "server name is " in line:
            print("Server name found")
            self.servername = line.split("server name is ")[1].strip()
