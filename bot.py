import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot instance with command prefix
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print('------')

@bot.event
async def on_message(message):
    """Called when a message is sent in any channel the bot can see."""
    # Don't respond to ourselves
    if message.author == bot.user:
        return
    
    print(f'Message from {message.author}: {message.content}')
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='ping')
async def ping(ctx):
    """Responds with the bot's latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! {latency}ms')

@bot.command(name='hello')
async def hello(ctx):
    """Greets the user."""
    await ctx.send(f'Hello, {ctx.author.name}!')

@bot.command(name='echo')
async def echo(ctx, *, message):
    """Echoes back the message."""
    await ctx.send(message)

@bot.command(name='help_custom')
async def help_custom(ctx):
    """Shows custom help information."""
    embed = discord.Embed(
        title='Bot Commands',
        description='Here are all available commands:',
        color=discord.Color.blue()
    )
    embed.add_field(name='!ping', value='Shows bot latency', inline=False)
    embed.add_field(name='!hello', value='Greets you', inline=False)
    embed.add_field(name='!echo [message]', value='Echoes your message', inline=False)
    embed.set_footer(text='Made with discord.py')
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handles command errors."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Missing required argument: {error.param}')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found. Use `!help_custom` for available commands.')
    else:
        await ctx.send(f'An error occurred: {error}')

# Run the bot
bot.run(TOKEN)