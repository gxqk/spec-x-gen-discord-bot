import discord
from discord import app_commands
from discord.ext import commands
from utils import config
import os

class Stock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.accounts_folder = "accounts"

    def count_accounts(self):
        services = {}
        
        if not os.path.exists(self.accounts_folder):
            return {}
            
        for filename in os.listdir(self.accounts_folder):
            if filename.endswith(".txt"):
                service_name = filename[:-4]
                try:
                    with open(os.path.join(self.accounts_folder, filename), 'r') as f:
                        count = sum(1 for line in f if line.strip())
                    services[service_name] = count
                except Exception as e:
                    print(f"Error while reading {filename}: {e}")
                    services[service_name] = 0
                    
        return services

    @app_commands.command(name="stock", description="Display available accounts stock")
    async def stock(self, interaction: discord.Interaction):
        services = self.count_accounts()
        
        if not services:
            embed = discord.Embed(
                title="❌ Error",
                description="No services available at the moment.",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="📊 Available Stock",
            description="",
            color=int(config['colors']['info'], 16)
        )
        
        for service, count in services.items():
            emoji = "🟢" if count > 0 else "🔴"
            embed.description += f"{emoji} **{service.upper()}** ➜ `{count} accounts`\n"
            
        embed.timestamp = discord.utils.utcnow()
        
        embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Stock(bot)) 