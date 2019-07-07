#TODO: Enable on release. IDK what this is
#import gevent.monkey
#gevent.monkey.patch_all()

from dota_bot import *
from utils import *
import community

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


class CommunityCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.ext.commands.dm_only()
    @command(
        name='register',
        help='Signup with !register <your_steam_id> <your_email>'
    )
    async def register(self, ctx, steam_id:int, email:str):
        if not community.valid_email(email):
            raise Exception('Invalid email!')

        if not community.valid_steam_id(steam_id):
            return Exception('Invalid steam ID!')

        community.register_player(ctx.author.id, steam_id, email)
        await ctx.send('{}: {} {} {}'.format(ctx.author.name, ctx.author.id, steam_id, email))

    async def cog_command_error(self, ctx, error):
        await ctx.send('\n{}\n{}'.format(
            error,
            ctx.command.help
            ))

    @command(
        name='lobby',
        help='Start a new lobby. Required argument is mode: <RD, CD, CM>.'
    )
    async def lobby(self, ctx, mode:str):
        pass

class DiscordManagementCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_role('admin')
    @command(
        name='clean',
        help='Clean chat history for current channel. Keeps pinned messages.'
    )
    async def clean(self, ctx):
        channel = ctx.channel
        messages = await channel.history().flatten()
        await channel.delete_messages([m for m in messages if not m.pinned])

    async def cog_command_error(self, ctx, error):
        await ctx.send('\n{}\n{}'.format(
            error,
            ctx.command.help
        ))

class DiscordBot(Bot):
    def __init__(self, token, *args, command_prefix='!', freq=0.1, **kwargs):
        Bot.__init__(self, command_prefix=command_prefix)

        self.token = token

        self.add_cog(CommunityCog(self))
        self.add_cog(DiscordManagementCog(self))

        self.cluster = DotaBotCluster(wait_dota=False)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task(freq=freq))

    async def my_background_task(self, freq=0.1):
        await self.wait_until_ready()
        #self.cluster.run_forever(freq=0.1)
        while not self.is_closed():
            self.cluster.idle()
            await asyncio.sleep(freq)

if __name__ == '__main__':
    bot = DiscordBot(cfg.discord.bot_token, freq=0.1)
    bot.run(cfg.discord.bot_token)
