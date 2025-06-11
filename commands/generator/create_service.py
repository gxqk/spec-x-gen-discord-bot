import discord
from discord import app_commands
from discord.ext import commands
from utils import config, is_whitelisted
import os

class CreateService(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.accounts_folder = "accounts"

    @app_commands.command(name="create_service", description="Create a new service")
    @is_whitelisted()
    @app_commands.describe(service="The name of the service to create")
    async def create_service(self, interaction: discord.Interaction, service: str):
        """Create a new service file in the accounts folder"""
        await interaction.response.defer(ephemeral=True)
        
        if not os.path.exists(self.accounts_folder):
            os.makedirs(self.accounts_folder)
        
        service = service.lower().strip()
        
        if not service.replace('_', '').replace('-', '').isalnum():
            embed = discord.Embed(
                title="❌ Error",
                description="> ⚠️ Service name can only contain letters, numbers, underscores and hyphens!",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
            
        filepath = os.path.join(self.accounts_folder, f"{service}.txt")
        if os.path.exists(filepath):
            embed = discord.Embed(
                title="❌ Error",
                description=f"> ⚠️ The service **{service.upper()}** already exists!",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
            
        try:
            with open(filepath, 'w') as f:
                pass
                
            embed = discord.Embed(
                title="✅ Service Created",
                description=f"> 📦 The service **{service.upper()}** has been created successfully!\n\n> 💡 You can now add accounts using the restock command.",
                color=int(config['colors']['success'], 16),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error creating service {service}: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="> ⚠️ An error occurred while creating the service.\n> Please contact an administrator.",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CreateService(bot)) 