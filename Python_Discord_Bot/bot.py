import os
import discord
import logging
import discord.utils as du
from discord.ext import commands
from discord.ext.commands import(has_permissions, MissingPermissions, MissingRole, MissingRequiredArgument, BadArgument, CommandInvokeError, TooManyArguments)
from pipenv.vendor.dotenv import load_dotenv
import time
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logger = logging.getLogger('awesomo')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='awesomo.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix = '!')


#------------------------------------------Events-------------------------------------------
# On Ready event prints to shell when bot comes online.
@client.event
async def on_ready():
    logger.info("Bot is ready")

# Used to identify inappropriate messages in chat and remove them.
inappropriate_words = [
    
]

dict = {
    'Author': 'author',
    'Strike Number': 0
}


def member_strike(strikes,author):
    if strikes >= 1:
        logger.warning(f'You need to kick {author} from the guild they have exceeded 1 inappropriate words.')
    dict['Strike Number'] = 0

# Message event monitors chat for the inappropriate words defined above, then deletes them.
@client.event
async def on_message(message):
    for slang in inappropriate_words:
        altered_slang = re.compile(re.escape(slang), re.IGNORECASE)
        message_containing_slang = altered_slang.sub(slang,message.content)
        
        if slang in message_containing_slang: 
            deleted_message = message.content
            author = message.author
            dict['Author'] = author
            dict['Strike Number'] += 1
            strikes = dict.get('Strike Number')

            logger.info(f'{author} said, "{deleted_message}". Strike #: {strikes}')
            await message.delete()
            member_strike(strikes,author)
            
    await client.process_commands(message)

# Member status event (prints to shell when a member has come online or gone offline)
@client.event
async def on_member_update(before,after):
    if str(after.status) == "online":
        logger.info("{} has come {}.".format(after.name,after.status))
    elif str(after.status) == "offline":
        logger.info("{} has gone {}.".format(after.name,after.status))

# Error handling event
@client.event
async def on_command_error(ctx,error):
    author_of_message = ctx.author.mention
    if isinstance(error,MissingRequiredArgument):
        await ctx.send(f'{author_of_message} make sure to include all required arguments.')
    elif isinstance(error,MissingPermissions):
        await ctx.send(f'{author_of_message} you do not have permission to run this command.')
    elif isinstance(error,MissingRole):
        await ctx.send(f'{author_of_message} you do not have the required role to run this command.')
    elif isinstance(error,CommandInvokeError):
        await ctx.send(f'{author_of_message} bot has encountered a problem with the command given. Contact the bot owner.')
    elif isinstance(error,TooManyArguments):
        await ctx.send(f'{author_of_message} you have provided too many arguments for the given command. Run "!commands" to see the syntax of the available commands.')

# -----------------Commands used for creating channels and categories----------------------
# createcategory command creates a new category
@client.command(name = 'createcategory', description = 'Creates a category with custom name. (Ex: !createcategory gaming)')
async def createcategory(ctx, category_name):
    guild = ctx.guild 
    await guild.create_category(category_name)
    logger.info(f'Category, {category_name} was created.')
    print('---------------------------------------------------------------')
    
# createtextchannel command creates a new text channel withing an existing category
@client.command(name='createtextchannel', description = 'Creates a text channel within a specified category (Ex: !createtextchannel categoryname txtchannelname).')
async def createchannel(ctx, category_name, channel_name):
    guild = ctx.guild
    author = ctx.author
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    category = discord.utils.get(guild.categories, name=category_name)
    if not existing_channel:
        logger.info(f'{author} created a new text channel: {channel_name} in category, {category_name}.')
        await guild.create_text_channel(channel_name, category = category)

# createvoicechannel command creates a new voice channel within an existing channel
@client.command(name='createvoicechannel', description = 'Creates a voice channel within a specified category (Ex: !createvoicechannel categoryname voicechannelname).')
async def createvoicechannel(ctx,category_name, channel_name):
    guild = ctx.guild
    author = ctx.author
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    category = discord.utils.get(guild.categories, name=category_name)
    if not existing_channel:
        logger.info(f'{author} created a new voice channel: {channel_name} in category, {category_name}.')
        await guild.create_voice_channel(channel_name, category = category)

# ---------------------Utility commands--------------------------------
# Clear command clears specified number of messages
@client.command(name='clear', description = 'Clears either 100 or specified number of messages in current channel. (Ex: !clear 10)')
async def clear(ctx, number_amount = 100):
    cast_number = int(number_amount)
    actual_number = cast_number + 1
    await ctx.channel.purge(limit = actual_number)
    logger.info(f'{number_amount} message(s) were removed from chat.')

# commands command returns the available custom commands and their descriptions
@client.command(name='commands', description='Returns all commands available. (Ex: !commands)')
async def commands(ctx):
    helptext = "```"
    space = "\n"
    for command in client.commands:
        helptext += f"!{command}: {command.description}\n" + space
    helptext += "```"
    await ctx.send(helptext)

# newnickname command creates a new nickname for the user specified
@has_permissions(administrator=True)
@client.command(name='newnickname', description = 'Gives new nickname to specified member. (Ex: !newnickname @username nickname)')
async def newnickname(ctx, member : discord.Member, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Member {member} nickname was changed to: {nick}')

# embed command returns an embed showing stats on the server
@client.command(name='embed', description='Shows an embed. (Ex: !embed)')
async def embed(ctx):
    guild = ctx.guild
    category = discord.CategoryChannel
    embed = discord.Embed(
        title = 'Server info',
        description = 'Description: Stats of server.',
        colour = discord.Colour.dark_green()
    )
    embed.set_author(name='Author: Joey C.',url='',icon_url='')
    embed.set_image(url='https://i.ytimg.com/vi/99wSfMyj8ak/hqdefault.jpg')
    embed.add_field(name='Server name',value=guild.name)
    embed.add_field(name='Server & Bot Owner',value=guild.owner)
    embed.add_field(name='Server Size',value=guild.member_count)

    await ctx.send(embed=embed)

# creates role for admin of the guild. 
@client.command(name='createadminrole', description='Creates a new role in the guild. (admin only)')
async def createadminrole(ctx, name):
    guild = ctx.guild
    user = ctx.message.author

    if ctx.author == ctx.guild.owner:
        all_perm = discord.Permissions.all()
        role_colour = discord.Colour.purple()

        await guild.create_role(name=name, permissions=all_perm, colour=role_colour, mentionable=True)
    
    role = discord.utils.get(ctx.guild.roles, name=name)
    await user.add_roles(role)

# creates a general role having text permissions on the server.
@has_permissions(administrator=True)
@client.command(name='creategeneraltextrole', description='Creates a general role in the guild having text permissions. (admin only)')
async def creategeneraltextrole(ctx, name):
    guild = ctx.guild

    message_permissions = discord.Permissions.text()
    role_colour = discord.Colour.dark_gray()

    await guild.create_role(name=name, permissions=message_permissions, colour=role_colour, mentionable=False)

# creates a general role having voice permissions on the server.
@has_permissions(administrator=True)
@client.command(name='creategeneralvoicerole', description='Creates a general role in the guild having voice permissions. (admin only)')
async def creategeneralvoicerole(ctx, name):
    guild = ctx.guild

    voice_permissions = discord.Permissions.voice()
    role_colour = discord.Colour.darker_gray()

    await guild.create_role(name=name, permissions=voice_permissions, colour=role_colour, mentionable=False)

# creates roles for members of the guild.
@has_permissions(administrator=True)
@client.command(name='assignrole', description='Creates a new role in the guild. (admin only)')
async def assignrole(ctx, member : discord.Member, role : discord.Role):
    await member.add_roles(role)
    logger.info(f'{member} now has the role of, {role}')


# ----------------- Commands that regulate server members and are only handed by server owner -------------------------
# kick command kicks the specified server member from the server
@has_permissions(administrator=True)
@client.command(name='kick', description = 'Kicks specified member. (Ex: !kick @user)')
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} was kicked for being themselves.')
    logger.info(f'{member} was kicked.')
    
# ban command bans the specified user from the server
@has_permissions(administrator=True)
@client.command(name='ban', description = 'Bans member from the server. (Ex: !ban @user)')
async def ban(ctx, member : discord.Member, reason=None):
    await member.ban(reason='Banned for being themselves.')
    await ctx.send(f'{member} was banned from the server for ruining the fun.')
    logger.info(f'{member} was banned from the server.')

# unban command unbans the specified user from the server
@has_permissions(administrator=True)
@client.command(name='unban', description='Unbans a user from the server. (!unban user#1234)')
async def unban(ctx, *, member):
    author = ctx.author.mention
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
  
    if (user.name, user.discriminator) == (member_name, member_discriminator):
        await ctx.guild.unban(user)
        await ctx.send(f'{author}, {member} has been unbanned from the server.')
        logger.info(f'{member} unbanned.')

# botlogoff command closes the bot
@has_permissions(administrator=True)
@client.command(name='botlogoff', description = 'Logs the bot off (only runnable by server Admin).')
async def botlogoff(ctx):
    author = ctx.author.mention
    try:
        await ctx.send(f'{author} logged me out. See ya later!')
        await client.logout()
        logger.info('Bot has logged off.')
    except RuntimeError:
        logger.warning("Error occurred when running botlogoff command.", exc_info=True)
        

# -------------------------------- Fun commands -----------------------------------
# steamsales command returns steam sales page
@client.command(name='steamsales', description = 'Provides a link to the sales currently on Steam. (Ex: !steamsales)')
async def steamsales(ctx):
    await ctx.send('https://store.steampowered.com/specials#p=0&tab=TopSellers')

# neweggsales command returns newegg dailydeals page
@client.command(name='neweggsales', description = 'Provides a link to the sales current on Newegg. (Ex: !neweggsales)')
async def hardwaresales(ctx):
    await ctx.send('https://www.newegg.com/todays-deals')

# Used for actually running the bot
client.run(TOKEN)
