from discord.ext import commands
import os
import sys
from dotenv import load_dotenv
import discord

# Cogs
import asyncio
import discord.ext.test as dpytest

# ----- General set up ------ #

PREFIX = '>>'
load_dotenv('.env')  # Load TOKEN
os.chdir("./data")  # Project directory

intents = discord.Intents(messages=True, members=True, guilds=True, presences=True, reactions=True)
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)  # Connection to Discord

# ----- Establish connection with server ------ #
if __name__ == "__main__":

    if len(sys.argv) >= 1 and sys.argv[0] != "init":
        print("This program just allows one argument: init")
        sys.exit()
    elif len(sys.argv) == 1 and sys.argv[0] == "init":

        if not os.path.isdir("data"):
            os.mkdir("data")

        ADMIN_ID = input("Please enter bot admin id: ")
        SERVER_ID = input("Please enter server id: ")

        f = open("ids.txt", "w")
        f.write(f"{ADMIN_ID}\n{SERVER_ID}")
        f.close()

    bot.load_extension("extension")
    bot.run(os.getenv('DISCORD_TOKEN'))
