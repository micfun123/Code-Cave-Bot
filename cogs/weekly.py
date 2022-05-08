import discord
from discord.ext import commands, tasks 
from discord.commands import slash_command
import random
import os
from datetime import datetime,time



class Weekly(commands.Cog):
    def __init__(self, client):
        self.client = client

   
    @commands.slash_command()
    async def suggest_challenge(self, ctx):
        channel = self.get_channel(967975366482362428)
        await channel.send(f"{ctx.author.mention} suggested a challenge!")
        await channel.send(f"{ctx.message.content}")
        await ctx.message.delete()
        await ctx.respond("Thanks for the suggestion!")

        
def setup(client):
    client.add_cog(Weekly(client))