import discord
from discord import app_commands
from discord.ext import commands
from utils import config, is_whitelisted
import os

class Restock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.accounts_folder = "accounts"

    def get_services(self):
        try:
            if not os.path.exists(self.accounts_folder):
                os.makedirs(self.accounts_folder)
                return []
                
            services = [
                f[:-4] for f in os.listdir(self.accounts_folder) 
                if f.endswith('.txt') and os.path.isfile(os.path.join(self.accounts_folder, f))
            ]
            return services
            
        except Exception as e:
            print(f"Error in get_services: {e}")
            return []

    @app_commands.command(name="restock", description="Announce a restock of accounts")
    @is_whitelisted()
    @app_commands.describe(
        service="The service that was restocked",
        amount="The number of accounts added"
    )
    async def restock(self, interaction: discord.Interaction, service: str, amount: int):
        service = service.lower()
        
        embed = discord.Embed(
            title="🎉 NEW RESTOCK!",
            color=int(config['colors']['success'], 16)
        )
        
        if config.get('restock_gif'):
            embed.set_image(url=config['restock_gif'])
            
        embed.description = f"""
> 📦 **Service**: `{service.upper()}`
> 🔢 **Amount**: `{amount} accounts`
> 🚀 **Available**: `Now`

> 💡 Use `/generate {service}` to generate an account!
"""
        
        embed.timestamp = discord.utils.utcnow()
        
        embed.set_footer(text=f"Restocked by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            
        await interaction.response.send_message(embed=embed)

    @restock.autocomplete('service')
    async def restock_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        try:
            services = self.get_services()
            
            return [
                app_commands.Choice(name=service.upper(), value=service)
                for service in services
                if current.lower() in service.lower()
            ][:25]
        except Exception as e:
            print(f"Error in autocomplete: {e}")
            return []

async def setup(bot: commands.Bot):
    await bot.add_cog(Restock(bot)) 