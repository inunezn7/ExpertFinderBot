import pytest
import discord.ext.test as dpytest
import discord
from discord.ext import commands
import os

os.chdir("./data")  # Project directory

@pytest.fixture
def bot(event_loop):

    PREFIX = '>>'
    #load_dotenv('.env')  # Load TOKEN
    print(os.getcwd())
    #os.chdir("./data")  # Project directory
    print(os.getcwd())

    intents = discord.Intents(messages=True, members=True, guilds=True, presences=True, reactions=True)
    bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None, event=event_loop)  # Connection to Discord
    bot.load_extension("extension")

    dpytest.configure(bot)
    return bot

"""
def pytest_sessionfinish():
    # Clean up attachment files
    files = glob.glob('./dpytest_*.dat')
    for path in files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error while deleting file {path}: {e}")
"""