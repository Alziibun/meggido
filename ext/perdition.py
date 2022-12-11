import discord

class Perdition:
    server_id = 1029286298156011600
    server = None
    channels = {
        "restart warnings" : 1029293109567307856,
        "whitelist feed"   : 1037514532639215626,
        "player list"      : 1036141105697271858,
    }

    @classmethod
    async def init(cls, bot: discord.Bot):
        cls.server = bot.get_guild(cls.server_id)
        for key, value in cls.channels.items():
            cls.channels[key] = bot.get_channel(value)
        print("Finished initializing server meta")
