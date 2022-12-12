import discord
import asyncio
import subprocess

start_file = "/opt/pzserver/start-server.sh"

class Server:
    process = None

    @classmethod
    async def start(cls):
        print("Starting process")
        cls.process = await asyncio.create_subprocess_shell(
            "bash /opt/pzserver/start-server.sh",
            stdin=asyncio.subprocess.PIPE,
        )
        print("Shell started")
        print("Commune passed.")

    @classmethod
    async def wait_until_ready(cls):
        while cls.process == None:
            await asyncio.sleep(1)

    @classmethod
    async def send(cls, cmd):
        stdout, stderr = await cls.process.communicate(input=cmd)
        if stdout:
            print(f"[SERVER] {stdout.decode()}")
        if stderr:
            print(f"[ERROR] {stdout.decode()}")

    @classmethod
    async def message(cls, message):
        await cls.send(f"servermsg \"{message}\"")

    @classmethod
    async def adduser(cls, username, password):
        await cls.send(f"adduser \"{username}\" \"{password}\"")

    @classmethod
    async def stop(cls):
        await cls.send(f"quit")

    @classmethod
    async def restart(cls):
        await cls.stop()
        while cls.process.returncode == None:
            pass
        await cls.start()