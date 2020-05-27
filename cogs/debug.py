import discord
import inspect
import io
import textwrap
import traceback

from contextlib import redirect_stdout
from discord.ext import commands
from PythonGists import PythonGists
from .utils.gets import getAgo, getChannel, getColor, getEmote, getGuild, getRole, getTimeDiff, getUser, getWithoutInvoke
from .utils.helper import edit, permEmbed
from .utils.save import delete_key, read_config, read_json, read_log, save_commands, save_config, save_log

###############
# Imports for Eval/Debug, I hate errors.
##############
import asyncio
import datetime
import gc
import json
import psutil
import random
import re
import time
import urllib

from bs4 import BeautifulSoup


class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()
        # I don't allow those errors to trigger me lol
        self.env = {
                    "asyncio": asyncio,
                    "datetime": datetime,
                    "gc": gc,
                    "json": json,
                    "psutil": psutil,
                    "random": random,
                    "re": re,
                    "time": time,
                    "urllib": urllib,
                    "BeautifulSoup": BeautifulSoup,
                    "discord": discord,
                    "edit": edit,
                    "getAgo": getAgo,
                    "getChannel": getChannel,
                    "getColor": getColor,
                    "getEmote": getEmote,
                    "getGuild": getGuild,
                    "getRole": getRole,
                    "getTimeDiff": getTimeDiff,
                    "getUser": getUser,
                    "getWithoutInvoke": getWithoutInvoke,
                    "permEmbed": permEmbed,
                    "delete_key": delete_key,
                    "read_config": read_config,
                    "read_json": read_json,
                    "read_log": read_log,
                    "save_commands": save_commands,
                    "save_config": save_config,
                    "save_log": save_log
                   }

    # DEBUG
    @commands.command(aliases=["Debug", "d", "D"])
    async def debug(self, ctx, *, code: str):
        """Single line Python debug.."""
        code = code.strip('` ')
        env = {
            'bot': self.bot,
            'say': ctx.send,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.guild,
            'server': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.message.author,
            'me': ctx.message.author,
            'self': self
        }

        env.update(self.env)
        env.update(globals())
        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            try:
                await ctx.message.add_reaction('\N{HEAVY MULTIPLICATION X}')
            except:
                pass
            await self.do_send(ctx=ctx, description="SelfBot Python Debug", value=str(type(e).__name__) + ': ' + str(e), filename='debug.py')
            return
        try:
            await ctx.message.add_reaction('\N{HEAVY CHECK MARK}')
        except:
            pass
        await self.do_send(ctx=ctx, description="SelfBot Python Debug", value=str(result), filename='debug.py')

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    async def do_send(self, ctx, description, value, filename):
        try:
            if len(str(value)) > 1990:
                link = PythonGists.Gist(description=description, content=str(value), name=filename)
                await ctx.send(content=f'\N{ROBOT FACE} I uploaded that for you!\n<{link}>')
            else:
                await ctx.send(f'```py\n{value}\n```')
        except discord.Forbidden:
            pass
        except discord.HTTPException as e:
            await ctx.send(content=f'\N{ROBOT FACE} Unexpected error: `{e}`')

    # Eval Command
    @commands.command(name='eval', aliases=["Eval", "e", "E"])
    async def _eval(self, ctx, *, body: str):
        """Multiline Python Eval."""
        env = {
            'bot': self.bot,
            'say': ctx.send,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.guild,
            'server': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.message.author,
            'me': ctx.message.author,
            'self': self,
            '_': self._last_result
        }

        env.update(self.env)
        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\N{HEAVY MULTIPLICATION X}')
            except:
                pass
            await self.do_send(ctx=ctx, description="SelfBot Python Eval Error", value=str(value) + str(traceback.format_exc()), filename='eval.py')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\N{HEAVY CHECK MARK}')
            except:
                pass

            if ret is None:
                if value:
                    await self.do_send(ctx=ctx, description="SelfBot Python Eval", value=str(value), filename='eval.py')
            else:
                self._last_result = ret
                await self.do_send(ctx=ctx, description="SelfBot Python Eval", value=str(value) + str(ret), filename='eval.py')

    @commands.command(aliases=["Repl"])
    async def repl(self, ctx):

        variables = {
            'bot': self.bot,
            'say': ctx.send,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.guild,
            'server': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.message.author,
            'me': ctx.message.author,
            'self': self,
            '_': self._last_result
        }

        variables.update(self.env)
        variables.update(globals())

        if ctx.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')
        while True:
            def check(m):
                return m.content.startswith('`') and m.channel.id == ctx.channel.id and m.author.id == ctx.me.id and not m.content.startswith('```py\n')
            response = await self.bot.wait_for('message', check=check)

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables['message'] = response
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                await self.do_send(ctx=ctx, description="SelfBot Python REPL Error", value=str(value) + str(traceback.format_exc()), filename='repl.py')
            else:
                value = stdout.getvalue()
                if result is not None:
                    await self.do_send(ctx=ctx, description="SelfBot Python REPL", value=str(value) + str(result), filename='repl.py')
                    variables['_'] = result
                elif value:
                    await self.do_send(ctx=ctx, description="SelfBot Python REPL", value=str(value), filename='repl.py')


def setup(bot):
    bot.add_cog(Debug(bot))
