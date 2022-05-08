import discord
from discord.ext import commands, tasks 
from discord.commands import slash_command
import random
import os
from datetime import datetime,time



class Weekly(commands.Cog):
    def __init__(self, client):
        self.client = client

   


@tasks.loop(time=time(10,00))
async def weekly_challenge(self):
    '''runs every day at 1PM UTC'''
    
    # check if the day is monday
    today = datetime.utcnow().isoweekday()
    if today == 5:  # Monday == 7
        channel = self.get_channel(967975366482362428)
        allmes = []
        async for message in channel.history(limit=200):
            allmes.append(message)
        randoms = random.choice(allmes)
        chennel2 = self.get_channel(967763538431082527)
        em = discord.Embed(title=f"weekly challenge",color=0x00ff00)
        em.description = "Its your favorite time of the week again!\n"
        em.add_field(name="Challenge :", value=randoms.content)
        msg = await channel.fetch_message(randoms.id)
        print(msg.content)
        await chennel2.send(embed=em)
        await chennel2.send(f'<@&959429849804595230>')
        await msg.delete()


        
def setup(client):
    client.add_cog(Weekly(client))