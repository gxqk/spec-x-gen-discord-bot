import discord
from discord.ext import commands
import json
import os
import asyncio
from discord import app_commands
from utils import config, stats

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)
        
    async def setup_hook(self):
        for file in os.listdir("commands/misc"):
            if file.endswith(".py") and not file.startswith("__"):
                await self.load_extension(f"commands.misc.{file[:-3]}")
                print(f"Command loaded: {file[:-3]}")
        
        for file in os.listdir("commands/generator"):
            if file.endswith(".py") and not file.startswith("__"):
                await self.load_extension(f"commands.generator.{file[:-3]}")
                print(f"Command loaded: {file[:-3]}")
        
        await self.tree.sync()

def check_whitelist(interaction: discord.Interaction) -> tuple[bool, str]:
    if str(interaction.guild_id) not in config['whitelist_guilds']:
        return False, "This server is not authorized to use this bot."
    
    if str(interaction.user.id) not in config['whitelist']:
        return False, "You are not in the whitelist!"
    
    return True, ""

def is_whitelisted():
    async def predicate(interaction: discord.Interaction) -> bool:
        is_allowed, message = check_whitelist(interaction)
        if not is_allowed:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

bot = Bot()

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name}')
    
    if config['status_type'].lower() == 'streaming':
        activity = discord.Activity(
            type=discord.ActivityType.streaming,
            name=f"{stats.total_generated} accounts generated"
        )
    else:
        activity = discord.Game(name=f"{stats.total_generated} accounts generated")
    
    await bot.change_presence(activity=activity)
    
    print("\nAuthorized servers:")
    for guild_id in config['whitelist_guilds']:
        guild = bot.get_guild(int(guild_id))
        if guild:
            print(f"- {guild.name} (ID: {guild.id})")
    
    print("\nAuthorized users:")
    for user_id in config['whitelist']:
        user = await bot.fetch_user(int(user_id))
        if user:
            print(f"- {user.name} (ID: {user.id})")

@bot.event
async def on_guild_join(guild):
    if str(guild.id) not in config['whitelist_guilds']:
        await guild.leave()
        print(f"Left unauthorized server: {guild.name} (ID: {guild.id})")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if str(message.channel.id) in [config['normal_channel_generation'], config['premium_channel_generation']]:
        if str(message.author.id) in config['whitelist']:
            await bot.process_commands(message)
            return
            
        try:
            await message.delete()
        except discord.Forbidden:
            print(f"Could not delete message in {message.channel.name}")
        except Exception as e:
            print(f"Error while deleting message: {e}")

    await bot.process_commands(message)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        pass
    else:
        await interaction.response.send_message(f"❌ An error occurred: {str(error)}", ephemeral=True)

bot.run(config['token'])