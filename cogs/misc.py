import aiohttp
import discord
import json
import logging
import mimetypes
import random
import re

from discord.ext import commands
from random import choice
from .utils.gets import getWithoutInvoke
from .utils.helper import edit, embedColor

log = logging.getLogger('LOG')


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ball = ["As I see it, yes", "It is certain", "It is decidedly so", "Most likely", "Outlook good",
                     "Signs point to yes", "Without a doubt", "Yes", "Yes – definitely", "You may rely on it", "Reply hazy, try again",
                     "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
        self.regionals = {'A': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'B': '\N{REGIONAL INDICATOR SYMBOL LETTER B}', 'C': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
                          'D': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'E': '\N{REGIONAL INDICATOR SYMBOL LETTER E}', 'F': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
                          'G': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'H': '\N{REGIONAL INDICATOR SYMBOL LETTER H}', 'I': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
                          'J': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'K': '\N{REGIONAL INDICATOR SYMBOL LETTER K}', 'L': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
                          'M': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'N': '\N{REGIONAL INDICATOR SYMBOL LETTER N}', 'O': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
                          'P': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'Q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}', 'R': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
                          'S': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 'T': '\N{REGIONAL INDICATOR SYMBOL LETTER T}', 'U': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
                          'V': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'W': '\N{REGIONAL INDICATOR SYMBOL LETTER W}', 'X': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
                          'Y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'Z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}', '!': '\u2757', '?': '\u2753', '+': '\u2795', '-': '\u2796'}
        self.numbers = {'0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣', '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣'}
        self.emoji_reg = re.compile(r'<:.+?:([0-9]{15,21})>')
        self.link = re.compile(r'^(?:http|ftp)s?://'
                               r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                               r'localhost|'
                               r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                               r'(?::\d+)?'
                               r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    # Sends a googleitfor.me link with the specified tags
    @commands.command(aliases=["L2g"])
    async def l2g(self, ctx, *, msg: str):
        """Links to lmgtfy."""
        lmgtfy = 'http://googleitfor.me/?q='
        words = msg.lower().strip().split(' ')
        for word in words:
            lmgtfy += word + '+'
        await edit(ctx, content=lmgtfy[:-1])

    # Picks a random answer from a list of options
    @commands.command(aliases=["Choose"])
    async def choose(self, ctx, *, choices: str):
        """Chooses one from many possibilities."""
        choiceslist = choices.split("|")
        choice = random.choice(choiceslist)
        if len(choiceslist) < 2:
            await edit(ctx, content="2+ Options, separated with ``|``",  ttl=5)
        else:
            em = discord.Embed()
            em.add_field(name="Options", value=choices, inline=False)
            em.add_field(name="Choice", value="🎲 | My Answer is ``{}``".format(choice))
            await edit(ctx, embed=em)

    # 8ball
    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, ctx, *, question: str):
        """Typical 8ball like you know it."""
        if question.endswith("?") and question != "?":
            await edit(ctx, content="`" + choice(self.ball) + "`")
        else:
            await edit(ctx, content="That doesn't look like a question.", ttl=3)

    # Urbandictionary
    @commands.command(aliases=["Urban"])
    async def urban(self, ctx, *, search_terms: str, definition_number: int=1):
        """Get an Urban Dictionary entry."""
        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11):
                pos = 0
        except ValueError:
            pos = 0
        search_terms = "+".join(search_terms)
        url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    result = json.loads(await r.text())
                    if result["list"]:
                        definition = result['list'][pos]['definition']
                        example = result['list'][pos]['example']
                        defs = len(result['list'])
                        embed = discord.Embed(title='Definition #{} out of {}'.format(pos + 1, defs), description=definition)
                        embed.set_author(name=search_terms, icon_url='https://i.imgur.com/bLf4CYz.png')
                        embed.add_field(name="Example:", value=example, inline=False)
                        await edit(ctx, embed=embed)
                    else:
                        await edit(ctx, content="Your search terms gave no results.", ttl=3)
        except IndexError:
            await edit(ctx, content="There is no definition #{}".format(pos + 1), ttl=3)
        except:
            await edit(ctx, content="Error.", ttl=3)

    @commands.command(aliases=["Gif"])
    async def gif(self, ctx, *text):
        """Get a gif from Giphy."""
        if text:
            if len(text[0]) > 1 and len(text[0]) < 20:
                try:
                    msg = "+".join(text)
                    search = "http://api.giphy.com/v1/gifs/search?q=" + msg + "&api_key=dc6zaTOxFJmzC"
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(search) as r:
                            result = json.loads(await r.text())
                            if result["data"] != []:
                                await edit(ctx, embed=discord.Embed().set_image(url=result["data"][0]["images"]["original"]["url"].split("?response")[0]))
                            else:
                                await edit(ctx, content="Your search terms gave no results.", ttl=3)
                except:
                    await edit(ctx, content="Error.", ttl=3)
            else:
                await edit(ctx, content="Invalid search.", ttl=3)
        else:
            await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Specify Search", ttl=3)

    def to_regionals(self, content, react):
        emote_list = []
        for i in content.split(" "):
            if self.emoji_reg.findall(i):
                emote_list.append(self.bot.get_emoji(int(self.emoji_reg.findall(i)[0])))
            else:
                for x in list(i):
                    if x.isalpha() or x in ('!', '?', '-', '+'):
                        emote_list.append(self.regionals[x.upper()])
                    elif x.isdigit():
                        emote_list.append(self.numbers[x])
                    elif react is False:
                        emote_list.append(x)
        return emote_list

    @commands.command(aliases=["React"])
    async def react(self, ctx):
        """React to a Message with Text."""
        await ctx.message.delete()
        reg = re.match(r'(\d{18})(?: )(.+)|(.+)', getWithoutInvoke(ctx))
        _id = reg.group(1)
        msg = reg.group(2) if reg.group(2) else reg.group(3)
        limit = 50 if _id else 1
        reactions = self.to_regionals(str(msg), True)
        async for message in ctx.message.channel.history(limit=limit):
            if (not _id and message.id != ctx.message.id) or (int(_id) == message.id):
                for i in reactions:
                    await message.add_reaction(i)

    @commands.command(aliases=["Regional", "Regionals", "regionals"])
    async def regional(self, ctx, *, msg: str):
        """Convert a Text to emotes."""
        regional_list = self.to_regionals(msg, False)
        regional_output = []
        for i in regional_list:
            regional_output.append(" ")
            if isinstance(i, discord.Emoji):
                regional_output.append(str(i))
            else:
                regional_output.append(i)
        await edit(ctx, content=''.join(regional_output))

    @commands.command(aliases=["Embed"])
    async def embed(self, ctx, *, msg: str):
        """Embed a Text."""
        try:
            await edit(ctx, embed=discord.Embed(description=msg))
        except:
            await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Something went wrong", ttl=5)

    @commands.command(aliases=["Eimage", "Ei", "ei"])
    async def eimage(self, ctx, *, msg: str):
        """Embed an image."""
        link = self.link.findall(msg)
        if link:
            mimetype, encoding = mimetypes.guess_type(link[0])
            if mimetype and mimetype.startswith('image'):
                try:
                    await edit(ctx, embed=discord.Embed().set_image(url=link[0]))
                except:
                    await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Something went wrong", ttl=5)
            else:
                await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} No image link", ttl=5)
        else:
            await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} No link given", ttl=5)


def setup(bot):
    bot.add_cog(Misc(bot))
