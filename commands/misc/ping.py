import discord
from discord import app_commands
from discord.ext import commands
from utils import config

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Test the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            emoji = "🟢"
            color = int(config['colors']['success'], 16)
        elif latency < 300:
            emoji = "🟡"
            color = int(config['colors']['info'], 16)
        else:
            emoji = "🔴"
            color = int(config['colors']['error'], 16)
            
        embed = discord.Embed(
            description=f"> {emoji} **{latency} ms**",
            color=color
        )
        embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot)) 