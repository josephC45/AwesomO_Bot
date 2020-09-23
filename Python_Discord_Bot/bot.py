import os
import discord
import discord.utils as du
from discord.ext import commands
from discord.ext.commands import(MissingRequiredArgument,BadArgument)
from pipenv.vendor.dotenv import load_dotenv
import time
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix = '!')

#------------------------------------------Events-------------------------------------------
# On Ready event prints to shell when bot comes online.
@client.event
async def on_ready():
    print("Bot is ready")
    print("----------------------------------------------------------")

# Used to identify inappropriate messages in chat and remove them.
inappropriate_words = [
    
    
]

def member_strike(dict,author):
    if dict['Strike Number'] > 0:
        print (f'You need to kick {author} from the guild they have exceeded 1 inappropriate words.')

# Message event monitors chat for the inappropriate words defined above, then deletes them.
@client.event
async def on_message(message):
    
    for slang in inappropriate_words:
        altered_slang = re.compile(re.escape(slang), re.IGNORECASE)
        message_containing_slang = altered_slang.sub(slang,message.content)
        if slang in message_containing_slang:
            counter = 0
            dict = {
                'Author': message.author,
                'Strike Number': counter
            }
            dict['Strike Number'] += 1
            counter = dict['Strike Number']
            deleted_message = message.content
            author = message.author

            print(f'{author} said, "{deleted_message}".')
            member_strike(dict,author)

            await message.delete()
    await client.process_commands(message)

# Member status event (prints to shell when a member has come online or gone offline)
@client.event
async def on_member_update(before,after):
    if str(after.status) == "online":
        print("{} has come {}.".format(after.name,after.status))
    elif str(after.status) == "offline":
        print("{} has gone {}.".format(after.name,after.status))
    print("---------------------------------------------------------------")

# Error handling event
@client.event
async def on_command_error(ctx,error):
    author_of_message = ctx.author.mention
    if isinstance(error,MissingRequiredArgument):
        await ctx.send(f'{author_of_message} make sure to include all required arguments.')

# -----------------Commands used for creating channels and categories----------------------
# createcategory command creates a new category
@client.command(name = 'createcategory', description = 'Creates a category with custom name. (Ex: !createcategory gaming)')
async def createcategory(ctx, category_name):
    guild = ctx.guild 
    await guild.create_category(category_name)
    print(f'Category, {category_name} was created.')
    print('---------------------------------------------------------------')
    
# createtextchannel command creates a new text channel withing an existing category
@client.command(name='createtextchannel', description = 'Creates a text channel within a specified category (Ex: !createtextchannel categoryname txtchannelname).')
async def createchannel(ctx, category_name, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    category = discord.utils.get(guild.categories, name=category_name)
    if not existing_channel:
        print(f'Creating a new text channel: {channel_name} in category, {category_name}.')
        await guild.create_text_channel(channel_name, category = category)

# createvoicechannel command creates a new voice channel within an existing channel
@client.command(name='createvoicechannel', description = 'Creates a voice channel within a specified category (Ex: !createvoicechannel categoryname voicechannelname).')
async def createvoicechannel(ctx,category_name, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    category = discord.utils.get(guild.categories, name=category_name)
    if not existing_channel:
        print(f'Creating a new voice channel: {channel_name} in category, {category_name}.')
        await guild.create_voice_channel(channel_name, category = category)

# ---------------------Utility commands--------------------------------
# Clear command clears specified number of messages
@client.command(name='clear', description = 'Clears either 100 or specified number of messages in current channel. (Ex: !clear 10)')
async def clear(ctx, number_amount = 100):
    cast_number = int(number_amount)
    actual_number = cast_number + 1
    await ctx.channel.purge(limit = actual_number)
    print(f'{number_amount} message(s) were removed from chat.')

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

# creates roles for members of the guild. 
@client.command(name='createrole', description='Creates a new role in the guild. (Ex: !createrole pcgamer)')
async def createrole(ctx, name):
    guild = ctx.guild
    user = ctx.message.author

    if ctx.author == ctx.guild.owner:
        all_perm = discord.Permissions.all()
        role_colour = discord.Colour.purple()

        await guild.create_role(name=name, permissions=all_perm, colour=role_colour, mentionable=True)
    
    role = discord.utils.get(ctx.guild.roles, name=name)
    await user.add_roles(role)

# ----------------- Commands that regulate server members and are only handed by server owner -------------------------
# kick command kicks the specified server member from the server
@client.command(name='kick', description = 'Kicks specified member. (Ex: !kick @user)')
async def kick(ctx, member : discord.Member, *, reason=None):
    if ctx.author == ctx.guild.owner:
    #discord.ext.commands.has_role('Admin'):
        await member.kick(reason=reason)
        await ctx.send(f'{member} was kicked for being themselves.')
    else:
        await ctx.send(f'You do not have permission to kick {member} only the server owner does.')

# ban command bans the specified user from the server
@client.command(name='ban', description = 'Bans member from the server. (Ex: !ban @user)')
async def ban(ctx, member : discord.Member, reason=None):
    if ctx.author == ctx.guild.owner:
        await member.ban(reason='Banned for being themselves.')
        await ctx.send(f'{member} was banned from the server for ruining the fun.')
    else:
        await ctx.send(f'You do not have permission to ban {member} only individuals with the role of Admin')

# unban command unbans the specified user from the server
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

# botlogoff command closes the bot
@client.command(name='botlogoff', description = 'Logs the bot off (only runnable by server Admin).')
async def botlogoff(ctx):
    if ctx.author == ctx.guild.owner:
        await ctx.send('Bot is shutting off in 10 seconds, plus the amount of time it takes to communicate with discords servers.')
        time.sleep(10)
        await client.close()
        print("Bot Closed")  # This is optional, but it is there to tell you.
    else:
        await ctx.send('You do not have permission to shut me off...')

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
