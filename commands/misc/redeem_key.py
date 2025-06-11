import discord
from discord import app_commands
from discord.ext import commands
from utils import config
import json
import os

class RedeemKey(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.keys_file = "resources/premium_key.txt"
        self.premium_file = "resources/premium.json"
        
        if not os.path.exists(self.premium_file):
            with open(self.premium_file, 'w') as f:
                json.dump({"premium_users": []}, f, indent=4)

    def is_key_valid(self, key: str) -> bool:
        if not os.path.exists(self.keys_file):
            return False
            
        with open(self.keys_file, 'r') as f:
            keys = [k.strip() for k in f.readlines()]
            return key in keys

    def remove_key(self, key: str):
        with open(self.keys_file, 'r') as f:
            keys = [k.strip() for k in f.readlines()]
            
        keys.remove(key)
        
        with open(self.keys_file, 'w') as f:
            f.write('\n'.join(keys) + ('\n' if keys else ''))

    def add_premium_user(self, user_id: str):
        with open(self.premium_file, 'r') as f:
            data = json.load(f)
            
        if user_id not in data["premium_users"]:
            data["premium_users"].append(user_id)
            
        with open(self.premium_file, 'w') as f:
            json.dump(data, f, indent=4)

    @app_commands.command(name="redeem_key", description="Use a premium key")
    @app_commands.describe(key="The premium key to use")
    async def redeem_key(self, interaction: discord.Interaction, key: str):
        await interaction.response.defer(ephemeral=True)
        
        member = interaction.guild.get_member(interaction.user.id)
        premium_role = interaction.guild.get_role(int(config['premium_role']))
        
        if premium_role in member.roles:
            embed = discord.Embed(
                title="❌ Error",
                description="> ⚠️ You are already premium!",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
            
        if not self.is_key_valid(key):
            embed = discord.Embed(
                title="❌ Error",
                description="> ❌ This premium key is not valid!",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
            
        try:
            await member.add_roles(premium_role)
            
            self.add_premium_user(str(interaction.user.id))
            
            self.remove_key(key)
            
            embed = discord.Embed(
                title="✨ Premium Activated!",
                description=f"> 🎉 Congratulations **{interaction.user.mention}**!\n> You are now premium!\n\n> 📝 Your key has been successfully activated.\n> ⭐ Enjoy your premium benefits!",
                color=int(config['colors']['success'], 16),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error during premium activation: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="> ⚠️ An error occurred while activating your premium.\n> Please contact an administrator.",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RedeemKey(bot)) 