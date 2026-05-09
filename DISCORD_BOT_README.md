# Discord Bot Template

A simple Discord bot template written in Python using discord.py.

## Requirements

- Python 3.8+
- discord.py
- python-dotenv

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Add your Discord bot token to `.env`

## Usage

Run the bot:
```bash
python bot.py
```

## Available Commands

- `!ping` - Shows bot latency
- `!hello` - Greets you
- `!echo [message]` - Echoes your message
- `!help_custom` - Shows all commands

## Creating Your Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" tab and click "Add Bot"
4. Copy the token and add it to `.env`
5. Go to OAuth2 > URL Generator
6. Select scopes: `bot`
7. Select permissions: `Send Messages`, `Read Message History`, etc.
8. Use the generated URL to invite the bot to your server

## Adding More Commands

Simply add new functions with the `@bot.command()` decorator:

```python
@bot.command(name='mycommand')
async def my_command(ctx):
    await ctx.send('Response')
```

## License

MIT