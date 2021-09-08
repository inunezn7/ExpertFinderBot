from gensim.models import KeyedVectors
from cogs.expertCog import Expert
from cogs.eventCog import Events
from cogs.scanCog import Scan
from cogs.otherCogs import OtherCommands
from cogs.helpCog import Help
import os
import sys
from cogs.aux_functions import *

def setup(bot):

    print(os.getcwd())
    #os.chdir("./data")  # Project directory
    print(os.getcwd())

    PREFIX = bot.command_prefix
    LOOP_TIME = 720  # Minutes between iterations
    N_EXPERTS = 5
    N_MIN_MENTIONS = 3
    SCAN_NUMBER = 1
    SIM_COEF = 0.6

    # ----- Channels IDs ------ #

    dicChannels = {}

    # Enter the ID of the server to scan messages
    # Also, it is needed to show the nickname of the user in that Server
    if not os.path.isfile("ids.txt"):
        print("File 'ids.txt' not found")
        sys.exit()

    f = open('ids.txt', 'r')
    lines = f.readlines()

    adminID = lines[0]
    GUILD_ID = lines[1]

    """
    adminID = 700809908861403286
    GUILD_ID = 223421264751099906  # Pharo Server
    #Nacho_server = 700810165447950396  # Pharo Server
    """

    # ----- Set up data ------ #

    try:
        with open('dictionaryMsgs.txt') as d:
            dicMsgs = json.load(d)
    except:
        dicMsgs = {}
        print("Messages dictionary not found")

    # Open concepts dictionary
    try:
        with open('dictionary.txt') as d:
            dicMentions = json.load(d)
    except:
        dicMentions = {}
        print("Mentions dictionary not found")

    # Load word embeddings
    try:
        pharo_w2v = KeyedVectors.load("pharo_w2v_200d.model", mmap='r')
    except:
        print("Word Embedding model not found")

    # Load users names
    try:
        with open('dictionaryNames.txt') as d:
            dicNames = json.load(d)
    except:
        dicNames = {}
        print("User Names dictionary not found")

    """ ---------------------------------------------
    Cogs
    --------------------------------------------- """

    bot.add_cog(Events(bot, dicChannels, GUILD_ID, PREFIX))
    bot.add_cog(
        Expert(bot, adminID, dicMsgs, dicMentions, dicNames, pharo_w2v, GUILD_ID, SIM_COEF, N_EXPERTS, N_MIN_MENTIONS))
    bot.add_cog(Scan(bot, adminID))
    bot.add_cog(OtherCommands(bot, adminID))
    bot.add_cog(Help(bot, adminID))
