import os
import inspect
import re

from utils.config import data as cfg

from steam import SteamID
from steam.client.builtins import User as SteamUser

#from discord import *
from discord.ext.commands.bot import *
from discord.ext.commands.core import *
#import discord
import asyncio

class MyCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    #discord.ext.commands.dm_only()
    @command(
        name='signup',
        help='Signup with !signup <your_steam_id> <your_email>'
    )
    async def signup(self, ctx, steam_id:int, email:str):
        if not MyCog.valid_email(email):
            raise Exception('Invalid email!')

        if not MyCog.valid_steam_id(steam_id):
            return Exception('Invalid steam ID!')

        await ctx.send('{}: {} {} {}'.format(ctx.author.name, ctx.author.id, steam_id, email))

    async def cog_command_error(self, ctx, error):
        await ctx.send('\n{}\n{}'.format(
            error,
            ctx.command.help
            ))

    @staticmethod
    def valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    @staticmethod
    def valid_steam_id(steam_id):
        valid = SteamID(steam_id).is_valid()

        user = SteamUser()

        return valid


class DiscordBot(Bot):
    def __init__(self, token, *args, command_prefix='!', **kwargs):
        Bot.__init__(self, command_prefix=command_prefix)

        self.token = token

        self.add_cog(MyCog(self))




if __name__ == '__main__':
    bot = DiscordBot(cfg.discord.bot_token)
    i=0
    while bot.loop:
        print(i)
        i+=1
    #bot.run_forever()
    try:
        bot.loop.run_until_complete(bot.start(cfg.discord.bot_token))
    except KeyboardInterrupt:
        bot.loop.run_until_complete(bot.logout())
        # cancel all tasks lingering
    finally:
        bot.loop.close()
    #bot.run(cfg.discord.bot_token)
