
import discord
from os import listdir
from os.path import isfile, join
import os
from dotenv import load_dotenv
from datetime import datetime,time
from rich.traceback import install

install()

load_dotenv()


from discord.ext import commands, tasks


client = commands.Bot(command_prefix= "^", case_insensitive=True)


@client.event
async def on_ready():
    # Setting `Playing ` status
    print("we have powered on, I an alive.")
    
    

TOKEN = os.getenv("TOKEN")

def start_bot(client):
    lst = [f for f in listdir("cogs/") if isfile(join("cogs/", f))]
    no_py = [s.replace('.py', '') for s in lst]
    startup_extensions = ["cogs." + no_py for no_py in no_py]
    try:
        for cogs in startup_extensions:
            client.load_extension(cogs)  # Startup all cogs
            print(f"Loaded {cogs}")

        print("\nAll Cogs Loaded\n===============\nLogging into Discord...")
        client.run(TOKEN) # Token do not change it here. Change it in the .env if you do not have a .env make a file and put DISCORD_TOKEN=Token 

    except Exception as e:
        print(
            f"\n###################\nPOSSIBLE FATAL ERROR:\n{e}\nTHIS MEANS THE BOT HAS NOT STARTED CORRECTLY!")



start_bot(client)

