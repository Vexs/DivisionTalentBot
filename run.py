#!/usr/bin/env python3

from discord.ext import commands
import discord
import re
import os
import aiohttp
from tokenfile import token
import inspect

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print('Bot ready!')
    print('Logged in as ' + bot.user.name)
    print('-------')

# this is all my standard bot boilerplate

def is_owner_check(message):
    return message.author.id == '129855424198475776' #Bot owner ID, used for technical


def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


@bot.command()
@is_owner()
async def load(extension_name: str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))


@bot.command()
@is_owner()
async def unload(extension_name: str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


@bot.command()
@is_owner()
async def reload(extension_name: str):
    bot.unload_extension(extension_name)
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} reloaded.".format(extension_name))

@bot.command(pass_context=True)
@is_owner()
async def upload(ctx, *, filename: str = None):
    def check(reaction, user):
        if user.id != ctx.message.author.id:
            return False
        return True
    try:
        file_url = ctx.message.attachments[0]['url']
    except IndexError:
        await bot.say('No file uploaded!')
        return
    if filename is None:
        filename = ctx.message.attachments[0]['filename']
    if '/' or '\\' in filename:
        filename = re.split(r"/|\\", filename)
    reaction_msg = await bot.say(
        'File URL is {}, with filename {}, is this okay? ✅/❌'.format(file_url, filename[-1]), delete_after=60)
    await bot.add_reaction(reaction_msg, '✅')
    await bot.add_reaction(reaction_msg, '❌')
    resp = await bot.wait_for_reaction(['✅', '❌'], message=reaction_msg, check=check, timeout=60)
    if resp is None:
        await bot.say('Timed out! Aborting!', delete_after=90)
    elif resp.reaction.emoji == '❌':
        await bot.say('Aborting!', delete_after=90)
    elif resp.reaction.emoji == '✅':
        try:
            await bot.clear_reactions(reaction_msg)
        except discord.Forbidden:
            pass
        try:
            file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), *filename)
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    content = await resp.read()
            with open(file_path, 'wb') as f:
                f.write(content)
            await bot.say('Successfully uploaded {}!'.format(filename[-1]), delete_after=30)
        except Exception as e:
            await bot.say(e)
    await bot.delete_message(ctx.message)

@bot.command(pass_context=True, hidden=True)
@is_owner()
async def debug( ctx, *, code: str):
    """Evaluates code."""
    code = code.strip('` ')
    python = '```py\n{}\n```'
    result = None
    env = {
        'bot': bot,
        'ctx': ctx,
        'message': ctx.message,
        'server': ctx.message.server,
        'channel': ctx.message.channel,
        'author': ctx.message.author
    }
    env.update(globals())
    try:
        result = eval(code, env)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await bot.say(python.format(type(e).__name__ + ': ' + str(e)))
        return
    await bot.say(python.format(result))


startup_extensions = ["talentlookup"]

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

bot.run(token, max_messages=5000)
