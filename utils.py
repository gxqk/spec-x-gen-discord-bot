import discord
from discord import app_commands
import json
import os
import time
import aiohttp
import asyncio

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

class Cooldowns:
    def __init__(self):
        self.cooldowns = {}
    
    def add_cooldown(self, user_id: str):
        if user_id in config['whitelist']:
            return
        self.cooldowns[user_id] = time.time()
    
    def add_premium_cooldown(self, user_id: str):
        if user_id in config['whitelist']:
            return
        self.cooldowns[user_id] = time.time()
    
    def get_remaining_time(self, user_id: str) -> int:
        if user_id in config['whitelist']:
            return 0
            
        if user_id not in self.cooldowns:
            return 0
        
        elapsed = time.time() - self.cooldowns[user_id]
        
        try:
            with open('resources/premium.json', 'r') as f:
                premium_data = json.load(f)
                is_premium = user_id in premium_data.get('premium_users', [])
        except:
            is_premium = False
        
        cooldown = config['premium_cooldown'] if is_premium else config['normal_cooldown']
        remaining = cooldown - elapsed
        
        if remaining <= 0:
            del self.cooldowns[user_id]
            return 0
            
        return int(remaining)

cooldowns = Cooldowns()

class Stats:
    def __init__(self):
        self.stats_file = "resources/stats.json"
        self.stats = self.load_stats()
        
    def load_stats(self):
        default_stats = {
            "total_generated": 0,
            "services": {},
            "user_stats": {}
        }
        if not os.path.exists(self.stats_file):
            return default_stats
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
                if "services" not in stats:
                    stats["services"] = {}
                if "user_stats" not in stats:
                    stats["user_stats"] = {}
                return stats
        except:
            return default_stats
            
    def save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=4)
            
    def increment_generated(self, service: str, user_id: str):
        self.stats["total_generated"] += 1
        
        if service not in self.stats["services"]:
            self.stats["services"][service] = 0
        self.stats["services"][service] += 1
        
        if user_id not in self.stats["user_stats"]:
            self.stats["user_stats"][user_id] = {}
        if service not in self.stats["user_stats"][user_id]:
            self.stats["user_stats"][user_id][service] = 0
            
        self.stats["user_stats"][user_id][service] += 1
        
        self.save_stats()
        return (
            self.stats["total_generated"],
            self.stats["services"][service],
            self.stats["user_stats"][user_id][service]
        )
        
    @property
    def total_generated(self):
        return self.stats["total_generated"]
        
    def get_service_count(self, service: str):
        return self.stats["services"].get(service, 0)
        
    def get_user_service_count(self, user_id: str, service: str):
        return self.stats["user_stats"].get(user_id, {}).get(service, 0)

stats = Stats()

def check_whitelist(interaction: discord.Interaction) -> tuple[bool, str]:
    if str(interaction.guild_id) not in config['whitelist_guilds']:
        return False, "This server is not authorized to use this bot."
    
    if str(interaction.user.id) not in config['whitelist']:
        return False, "You are not whitelisted!"
    
    return True, ""

def check_channel(interaction: discord.Interaction) -> tuple[bool, str]:
    if str(interaction.channel_id) != config['normal_channel_generation']:
        return False, f"This command can only be used in channel <#{config['normal_channel_generation']}>"
    return True, ""

def is_whitelisted():
    async def predicate(interaction: discord.Interaction) -> bool:
        is_allowed, message = check_whitelist(interaction)
        if not is_allowed:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            return False
            
        is_allowed, message = check_channel(interaction)
        if not is_allowed:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            return False
            
        return True
    return app_commands.check(predicate) 