import aiohttp
import datetime
import discord
import json
import logging
import unicodedata

from dateutil import parser
from discord.ext import commands
from .utils.gets import getAgo, getChannel, getEmote, getGuild, getRole, getUser, getWithoutInvoke
from .utils.helper import edit, embedColor

log = logging.getLogger('LOG')


class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # About this Selfbot
    @commands.command(aliases=["About"])
    async def about(self, ctx):
        """Infos about the SelfBot."""
        embed = discord.Embed()
        embed.set_author(name="Keanu's Selfbot", url="https://github.com/TKLProjects/TKL-Selfbot")
        embed.description = "https://github.com/TKLProjects/TKL-Selfbot\nThis is a Selfbot written by IgneelDxD#6666 and fixed by Keanu#2871"
        embed.colour = discord.Color.purple()

        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://api.github.com/repos/TKLProjects/TKL-SelfBot/commits") as resp:
                result = json.loads(await resp.text())
                form = '[``{0}``](https://github.com/TKLProjects/TKL-SelfBot/commit/{0}) {1} ({2})'
                com0 = form.format(result[0]['sha'][:7], result[0]['commit']['message'], getAgo(parser.parse(result[0]['commit']['author']['date'], ignoretz=True)))
                com1 = form.format(result[1]['sha'][:7], result[1]['commit']['message'], getAgo(parser.parse(result[1]['commit']['author']['date'], ignoretz=True)))
                embed.add_field(name='Latest Changes', value=f'{com0}\n{com1}')
        embed.set_thumbnail(url="https://i.imgur.com/cD51k3R.png")
        embed.set_footer(text='Made with discord.py | rewrite is the future!', icon_url='https://i.imgur.com/MyEXmz8.png')
        await edit(ctx, embed=embed)

    # User info on Server
    @commands.command(aliases=["User"])
    async def user(self, ctx):
        """Infos about a User/Member."""
        mem = getUser(ctx, getWithoutInvoke(ctx))
        if mem:
            em = discord.Embed(timestamp=datetime.datetime.now())
            em.colour = mem.colour
            em.add_field(name='User ID', value=mem.id, inline=True)
            if ctx.guild:
                if mem.activity:
                    em.description = 'Playing **%s**' % mem.activity
                em.add_field(name='Status', value=mem.status, inline=True)
                em.add_field(name='Nick', value=mem.nick, inline=True)
                em.add_field(name='In Voice', value=mem.voice,  inline=True)
            if not mem.bot:
                pro = await mem.profile()
                em.add_field(name='Partnership', value=str(mem.relationship.type)[17:].title() if mem.relationship is not None else None,  inline=True)
                em.add_field(name='Nitro', value='{}\n{}'.format(pro.premium_since.__format__('%d/%m/%Y'), getAgo(pro.premium_since)) if pro.premium is True else None,  inline=True)
            em.add_field(name='Account Created', value='%s\n%s' % (mem.created_at.__format__('%d/%m/%Y'), getAgo(mem.created_at)), inline=True)
            if ctx.guild:
                em.add_field(name='Join Date', value='%s\n%s' % (mem.joined_at.__format__('%d/%m/%Y'), getAgo(mem.joined_at)), inline=True)

                rolelist = ', '.join(r.name for r in mem.roles)
                if rolelist[11:]:
                    em.add_field(name='Roles [%s]' % (len(mem.roles) - 1), value=rolelist[11:], inline=True)

            guildlist = ', '.join(g.name for g in self.bot.guilds if g.get_member(mem.id))
            if (mem.id is not ctx.message.author.id) and guildlist:
                em.add_field(name='Shared Guilds [%s]' % len(guildlist.split(',')), value='%s' % guildlist, inline=True)
            em.set_thumbnail(url=mem.avatar_url)
            em.set_author(name=mem, icon_url='https://i.imgur.com/RHagTDg.png')
            await edit(ctx, embed=em, ttl=20)
        else:
            await edit(ctx, "\N{HEAVY EXCLAMATION MARK SYMBOL} User not found",  ttl=5)

    # User Avi on Server
    @commands.command(aliases=["Avi", "Avatar", "avatar"])
    async def avi(self, ctx):
        """Show the Avi of a User."""
        mem = getUser(ctx, getWithoutInvoke(ctx))
        if mem is not None:
            em = discord.Embed(timestamp=datetime.datetime.now())
            em.colour = mem.colour
            em.set_image(url=mem.avatar_url)
            em.set_author(name=mem, icon_url='https://i.imgur.com/RHagTDg.png')
            await edit(ctx, embed=em, ttl=20)
        else:
            await edit(ctx, "\N{HEAVY EXCLAMATION MARK SYMBOL} User not found",  ttl=5)

    # Roleinfo on Server
    @commands.command(aliases=["Role"])
    @commands.guild_only()
    async def role(self, ctx):
        """Info about a role."""
        role = getRole(ctx, getWithoutInvoke(ctx))
        if role is not None:
            em = discord.Embed(timestamp=datetime.datetime.now(), colour=role.colour)
            em.add_field(name='Name', value=role.name, inline=True)
            em.add_field(name='ID', value=role.id, inline=True)
            em.add_field(name='Created On', value='{}\n{}'.format(role.created_at.__format__('%d/%m/%Y'), getAgo(role.created_at)), inline=True)
            em.add_field(name='Color', value='{}\n{}'.format(str(role.colour).upper(), str(role.colour.to_tuple())[1:-1]), inline=True)
            em.add_field(name='Mentionable', value=role.mentionable,  inline=True)
            em.add_field(name='Members [%s]' % len(role.members), value='%s Online' % sum(1 for m in role.members if m.status != discord.Status.offline), inline=True)
            em.set_thumbnail(url='http://www.colorhexa.com/%s.png' % str(role.colour).strip("#"))
            await edit(ctx, embed=em, ttl=20)
        else:
            await edit(ctx, "\N{HEAVY EXCLAMATION MARK SYMBOL} Role not found",  ttl=5)

    # Serverinfo on Server
    @commands.command(aliases=["server", "Guild", "Server"])
    async def guild(self, ctx):
        """Infos about a Guild."""
        serv = getGuild(ctx, getWithoutInvoke(ctx))
        if serv:
            em = discord.Embed(timestamp=datetime.datetime.now())
            em.colour = ctx.message.author.colour
            em.set_author(name=serv.name, icon_url='https://i.imgur.com/RHagTDg.png')
            em.set_thumbnail(url=serv.icon_url)
            em.add_field(name='Owner', value='%s' % serv.owner,  inline=True)
            em.add_field(name='Created On', value='{}\n{}'.format(serv.created_at.__format__('%d/%m/%Y'), getAgo(serv.created_at)), inline=True)
            em.add_field(name='Region', value=serv.region, inline=True)
            em.add_field(name='ID', value=serv.id, inline=True)
            em.add_field(name='Verification Level', value=serv.verification_level, inline=True)
            em.add_field(name='2FA Requirement', value="True" if serv.mfa_level == 1 else "False", inline=True)
            em.add_field(name='Members [%s]' % serv.member_count, value='%s Online' % sum(1 for m in serv.members if m.status != discord.Status.offline), inline=True)
            em.add_field(name='Channels [%s]' % len(serv.channels), value='%s Text | %s Voice' % (len(serv.text_channels), len(serv.voice_channels)), inline=True)
            await edit(ctx, embed=em, ttl=20)
        else:
            await edit(ctx, "\N{HEAVY EXCLAMATION MARK SYMBOL} Guild not found",  ttl=5)

    # Server roles on Server
    @commands.command(aliases=["Roles"])
    @commands.guild_only()
    async def roles(self, ctx):
        """Show the roles on a guild."""
        serv = getGuild(ctx, getWithoutInvoke(ctx))
        if serv:
            em = discord.Embed(timestamp=datetime.datetime.now(), colour=ctx.message.author.colour)
            em.add_field(name='Roles [%s]' % (len(serv.roles) - 1), value=', '.join(r.name for r in serv.roles)[:-11], inline=False)
            await edit(ctx, embed=em, ttl=20)
        else:
            await edit(ctx, "\N{HEAVY EXCLAMATION MARK SYMBOL} Guild not found",  ttl=5)

    # Channel on Server
    @commands.command(aliases=["Channel"])
    async def channel(self, ctx):
        """Infos about a Channel."""
        channel = getChannel(ctx, getWithoutInvoke(ctx))
        if channel:
            em = discord.Embed(timestamp=datetime.datetime.now())
            em.colour = ctx.message.author.colour
            em.set_author(name=channel.name, icon_url='https://i.imgur.com/RHagTDg.png')
            em.add_field(name='ID', value=channel.id, inline=True)
            em.add_field(name='Created On', value='{}, {}'.format(channel.created_at.__format__('%d/%m/%Y'), getAgo(channel.created_at)), inline=True)
            if not isinstance(ctx.channel, discord.GroupChannel):
                em.add_field(name='Topic', value=channel.topic if channel.topic != "" else "None",  inline=False)
                em.add_field(name='NSFW', value='False' if bool(channel.is_nsfw()) is False else 'True', inline=True)
                em.add_field(name='Members [%s]' % len(channel.members), value='%s Online' % sum(1 for m in channel.members if m.status != discord.Status.offline), inline=True)
            else:
                if channel.icon is not None:
                    em.set_thumbnail(url=channel.icon_url)
                em.add_field(name='Owner', value=channel.owner, inline=True)
                em.add_field(name='Members', value=', '.join(c.name for c in channel.recipients), inline=True)
            await edit(ctx, embed=em, ttl=20)
        else:
            await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Channel not found",  ttl=5)

    # Emotes from Server
    @commands.command(aliases=["Emotes"])
    @commands.guild_only()
    async def emotes(self, ctx):
        """Display all emotes avaiable on a Server."""
        unique_emojis = set(ctx.message.guild.emojis)
        em = discord.Embed(timestamp=datetime.datetime.now(), title='Emotes [%s]' % len(unique_emojis), colour=ctx.message.author.colour)
        if unique_emojis:
            fields = []
            field = ''
            for i, emote in enumerate(unique_emojis, 1):
                if (len(field + str(emote) + ' ')) <= 1024:
                    field += str(emote) + ' '
                    if i == len(unique_emojis):
                        fields.append(field)
                else:
                    fields.append(field)
                    field = str(emote) + ' '
            for i in fields:
                em.add_field(name='﻿', value=i, inline=False)
        else:
            em.add_field(name='Emotes', value='Not Found \N{HEAVY EXCLAMATION MARK SYMBOL}', inline=False)
        await edit(ctx, embed=em, ttl=20)

    # Info of Custom or Unicode Emotes
    @commands.command(aliases=["Emote", "Emoji", "emoji"])
    async def emote(self, ctx, emote: str):
        """Infos about Emotes."""
        custom_emote = getEmote(ctx, getWithoutInvoke(ctx))
        if custom_emote:
            date = custom_emote.created_at.__format__('%d/%m/%Y')
            e = discord.Embed(title='Custom Emote')
            e.description = '**Name: **{1}\n**ID: **{2}\n**Server: **{0}\n**Created at: **{3}, {4}\n**Image: **[link]({5})'.format(custom_emote.guild.name, custom_emote.name, custom_emote.id, date, getAgo(custom_emote.created_at), custom_emote.url)
            e.set_thumbnail(url=custom_emote.url)
            await edit(ctx, embed=e)
        else:
            split = '\n'.join(emote).split('\n')
            e = discord.Embed(title='Unicode Emote {}'.format(emote))
            desc = ''
            if len(split) > 1:
                desc += '**Parts:**\n'
                for i in split:
                    desc += '{0} - `\\U{2:>08}` - {1}\nhttp://www.fileformat.info/info/unicode/char/{2}\n'.format(unicodedata.name(i), i, format(ord(i), 'x'))
            else:
                desc += '{0} - `\\U{1:>08}`\nhttp://www.fileformat.info/info/unicode/char/{1}\n'.format(unicodedata.name(split[0]), format(ord(split[0]), 'x'))
            e.description = desc
            if len(emote) > 20:
                await edit(ctx, content='\N{HEAVY EXCLAMATION MARK SYMBOL} Come on, only 20 chars...', ttl=3)
            else:
                await edit(ctx, embed=e)


def setup(bot):
    bot.add_cog(Info(bot))
