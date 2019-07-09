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

        #self.bot.bg_tasks.append(self.bot.loop.create_task(self.vouching(freq=5)))

    @discord.ext.commands.dm_only()
    @command(
        name='register',
        help='Signup with !register <your_steam_id> <your_mail>'
    )
    async def register(self, ctx, steam_id:int, mail:str):
        e = None
        if not community.valid_mail(mail):
            e = Exception('Invalid mail!')

        if not community.valid_steam_id(steam_id):
            e = Exception('Invalid steam ID!')

        if not community.is_new_user(ctx.author.id, steam_id, mail):
            e = Exception('User already registered, wait for vouching!')

        if e:
            #self.cog_command_error(ctx, e, ommit_help=True)
            raise e

        community.register_player(ctx.author.id, steam_id, mail)
        await ctx.send((
            'Successful registration!\n'
            'Wait for vouching process to complete.\n'
            'Your information:\n'
            '{}:'
            '\n\tDiscord ID: {}'
            '\n\tSteam ID: {}'
            '\n\tEmail: {}'
        ).format(ctx.author.name, ctx.author.id, steam_id, mail))

    async def cog_command_error(self, ctx, error, ommit_help=False):
        print(error)
        await ctx.send('```ERROR:\n{}\n\nCommand info:\n{}```'.format(
            error.original,
            ctx.command.help if not ommit_help else ''
            ))

    @command(
        name='lobby',
        help='Start a new lobby. Required argument is mode: <RD, CD, CM>.'
    )
    async def lobby(self, ctx, mode:str):
        pass

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print('Reaction!!!', payload)

    '''
    @on_reaction_add(reaction, user)
    async def vouching(self, freq=5):
        await self.bot.wait_until_ready()
        vouch_channel = self.bot.get_channel(cfg.discord.channels.vouching)
        while not self.bot.is_closed():
            pending = community.User.fetch_pending()
            print(pending)
            for p in pending:
                print(p)
                await vouch_channel.send('Pending user {}'.format(p.discord_id))
            await asyncio.sleep(freq)
    '''
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
    def __init__(self, token, *args, command_prefix='!', freq=0.1, run_bots=True, **kwargs):
        Bot.__init__(self, command_prefix=command_prefix)

        self.token = token

        self.bg_tasks = list()

        self.add_cog(CommunityCog(self))
        self.add_cog(DiscordManagementCog(self))

        if run_bots:
            self.cluster = DotaBotCluster(wait_dota=False)
            # create the background task and run it in the background
            bg_tasks.append(self.loop.create_task(self.dota_bots_idle(freq=freq)))
    
    async def dota_bots_idle(self, freq=0.1):
        await self.wait_until_ready()
        while not self.is_closed():
            self.cluster.idle()
            await asyncio.sleep(freq)

if __name__ == '__main__':
    bot = DiscordBot(cfg.discord.bot_token, freq=0.1, run_bots=False)
    bot.run(cfg.discord.bot_token)
