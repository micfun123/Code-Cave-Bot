import discord
from discord.ext import commands

class TestCog(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    async def test(self, ctx):
        await ctx.send("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

def setup(client):
    client.add_cog(TestCog(client))