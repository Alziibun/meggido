import discord

from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = discord.Bot(intents=intents, debug_guilds=[1029286298156011600])

if __name__ == "__main__":
    for ex in extensions:
        try:
            bot.load_extension(ex)
            print(ex, 'loaded.')
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(ex, exc))
    with open ('key', 'r') as key:
        bot.run(key.readline())