from discord import app_commands
from discord.ext import commands
import discord
from utils import config, is_whitelisted, stats, cooldowns
import os
import random

class Generate(commands.Cog):
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

    def get_account(self, service: str) -> tuple[bool, str, list[str]]:
        filepath = os.path.join(self.accounts_folder, f"{service}.txt")
        
        if not os.path.exists(filepath):
            return False, "This service doesn't exist.", []
            
        try:
            with open(filepath, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
            if not lines:
                return False, "No more accounts available for this service.", []
                
            account = random.choice(lines)
            lines.remove(account)
            
            with open(filepath, 'w') as f:
                f.write('\n'.join(lines))
                
            return True, account, lines
        except Exception as e:
            print(f"Error while generating account for {service}: {e}")
            return False, "An error occurred while generating the account.", []

    @app_commands.command(name="generate", description="Generate an account for the requested service")
    @app_commands.describe(service="The service to generate an account for")
    async def generate(self, interaction: discord.Interaction, service: str):
        await interaction.response.defer(ephemeral=False)
        
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Command Blocked",
                description="> 🔒 Generation in DMs is a premium feature!\n\n> ⭐ **Premium Benefits**:\n> • DM Generation\n> • Reduced cooldown (1 minute)\n> • Exclusive `/p_gen` command\n> • Regular drops of accounts in large quantities\n\n> 💎 To become premium, use the `/redeem_key` command with a premium key!",
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if str(interaction.user.id) not in config['whitelist']:
            if str(interaction.channel_id) != config['normal_channel_generation']:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"> ⚠️ This command can only be used in <#{config['normal_channel_generation']}>",
                    color=int(config['colors']['error'], 16)
                )
                embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        
        if str(interaction.user.id) not in config['whitelist']:
            remaining = cooldowns.get_remaining_time(str(interaction.user.id))
            if remaining > 0:
                minutes = remaining // 60
                seconds = remaining % 60
                
                embed = discord.Embed(
                    title="⏳ Active Cooldown",
                    description=f"> ⌛ You must wait **{minutes}m {seconds}s** before generating a new account!",
                    color=int(config['colors']['error'], 16)
                )
                if config.get('cooldown_gif'):
                    embed.set_image(url=config['cooldown_gif'])
                embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        
        service = service.lower()
        success, account, remaining = self.get_account(service)
        
        if not success:
            embed = discord.Embed(
                title="❌ Error",
                description=account,
                color=int(config['colors']['error'], 16)
            )
            embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
            
        try:
            cooldowns.add_cooldown(str(interaction.user.id))
            
            total, service_total, user_count = stats.increment_generated(service, str(interaction.user.id))
            
            if config['status_type'].lower() == 'streaming':
                activity = discord.Activity(
                    type=discord.ActivityType.streaming,
                    name=f"{total} accounts generated"
                )
            else:
                activity = discord.Game(name=f"{total} accounts generated")
            
            await self.bot.change_presence(activity=activity)
            
            account_parts = account.split(':', 1)
            username = account_parts[0] if len(account_parts) > 0 else "N/A"
            
            if len(account_parts) > 1:
                password_parts = account_parts[1].split(' ', 1)
                password = password_parts[0]
                additional_info = password_parts[1] if len(password_parts) > 1 else ""
            else:
                password = "N/A"
                additional_info = ""
            
            dm_embed = discord.Embed(
                title=f"🎉 {service.upper()} Account Generated",
                description=f"> 🔢 This is your **{user_count}th** {service.upper()} account generated!",
                color=int(config['colors']['success'], 16),
                timestamp=discord.utils.utcnow()
            )
            dm_embed.add_field(name="📧 Username/Email", value=f"```{username}```", inline=False)
            dm_embed.add_field(name="🔑 Password", value=f"```{password}```", inline=False)
            if additional_info:
                dm_embed.add_field(name="ℹ️ Additional Info", value=f"```{additional_info}```", inline=False)
            dm_embed.add_field(name="📋 Full Combo", value=f"```{account}```", inline=False)
            dm_embed.add_field(name="📝 Note", value="> If the account doesn't work, don't panic. It happens sometimes.", inline=False)
            dm_embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.user.send(embed=dm_embed)
            
            success_embed = discord.Embed(
                title="✅ Generation Successful!",
                description=f"> 📨 **{interaction.user.mention}**, your **{service.upper()}** account has been sent to your DMs!\n\n> ℹ️ If you didn't receive the message, check that your DMs are enabled for this server.\n\n> 📊 `{len(remaining)}` accounts remaining.",
                color=int(config['colors']['success'], 16),
                timestamp=discord.utils.utcnow()
            )
            if config.get('generate_gif'):
                success_embed.set_image(url=config['generate_gif'])
            success_embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            
            await interaction.followup.send(embed=success_embed, ephemeral=False)
            
        except discord.Forbidden:
            error_embed = discord.Embed(
                title="⚠️ DMs Disabled",
                description=f"> ❌ **{interaction.user.mention}**, unable to send the account to your DMs!\n\n> 💡 **How to enable DMs**:\n> 1. Right-click on the server\n> 2. Privacy Settings\n> 3. Allow Direct Messages\n\n> ⚠️ Once enabled, use the command again.",
                color=int(config['colors']['error'], 16)
            )
            error_embed.set_footer(text=f"Executed by {interaction.user} | gxqk the best", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @generate.autocomplete('service')
    async def generate_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
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
    await bot.add_cog(Generate(bot)) 