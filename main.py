from discord.ext import commands, tasks
import discord
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import timedelta, datetime, timezone
import json
import Encoder
import operator


# ----- Set up ------ #
load_dotenv('.env')  # Load TOKEN
intents = discord.Intents(messages=True, members=True, guilds=True)
bot = commands.Bot(command_prefix='!', intents=intents) # Connection to Discord
os.chdir("/Users/Nacho/Desktop/ChatBot Project/")   # Project directory
LOOP_TIME = 5  # Minutes between iterations
#dic = {}

# ----- Users IDs ------ #
nachoID = 700809908861403286

# ----- Channels IDs ------ #
dicChannels = {}
dicChannels["Nacho_general"] = 700810165447950399
# dicChannels["ISCLab_general"] = 484788823444946965
# dicChannels["ISCLab_pharo"] = 485114368644612097
# dicChannels["ISCLab_vr"] = 689530665531736114

# Choosing a Channel
#idChannel = dicChannels["Nacho_general"]

# This is temporary, to be able to choose a channel and don't get the messages of the irrelevant ones.
# Later on, it might be useful to improve this system.


# ----- On_ready event ------ #
@bot.event
async def on_ready():  # on_ready is called when the client is done preparing the data received from Discord
    print('We have logged in as {0.user}'.format(bot))  # In response, print something
    for server in bot.guilds:
        print("\n", server.name)
        for ch in server.channels:
            print(ch)
            print(ch.id)
    print(datetime.now())
    scanEvery.start()


# ----- On_message event ------ #
@bot.event
async def on_message(msg):  # It is called when the bot receives a message
    if msg.author == bot.user:  # To check the message was not sent by ourselves.
        return

    elif msg.content.startswith('$hello'):
        await msg.channel.send('Hello!')

    await bot.process_commands(msg)  # This line is necessary to allow the bot to hear the commands after
                                     # receive the on_message event.


@bot.command(name='expert', help='Need an expert? Write a key concept you want to find one in')
async def expert(ctx, concept):

    with open('dictionary.txt') as d:
        dic = json.load(d)
    with open('dictionaryNames.txt') as d:
        dicNames = json.load(d)

    if concept not in dic:
        await ctx.send("So sorry, your concept has not be mentioned in this server")
        return

    usersList = dic[concept]
    experts = []
    count = 0
    l = len(usersList)
    for users in range(l):
        e = max(usersList.items(), key=operator.itemgetter(1))[0]
        usersList.pop(e)
        experts.append(e)
        count += 1
        if count > 5:
            break

    output = []
    for e in experts:
        exp = dicNames[e]
        output.append(exp[1] + " @" + exp[0])

    embedVar = discord.Embed(title="Experts for " + str(concept),
                             description="\n".join(output),
                             color=0x00ff00)

    await ctx.send(embed=embedVar)


@bot.command(name='scanFromScratch', help='Scan messages from every Channel from the start of the server until now')
async def scanFromScratch(ctx):

    # Check if the user can use the command
    if ctx.author.id != nachoID:
        await ctx.send("I'm sorry, you are not allowed to use this command :(")
        return

    await scan(datetime(2016, 1, 1, 0, 0, 0, 0), datetime.utcnow(), append=False)  # A long time ago year. To scan all the messages from the server
    await ctx.send("Scan completed")


# Command
@bot.command(name='scanCommand', help='Scan messages from every Channel since last time server was scanned')
async def scanCommand(ctx):

    # Check if the user can use the command
    if ctx.author.id != nachoID:
        await ctx.send("I'm sorry, you are not allowed to use this command :(")
        return

    await scanSinceLastUpdate()
    await ctx.send("Scan completed")


# Scan messages after the bot was not active for a while
# Function
async def scanSinceLastUpdate():

    f = open("LastUpdated.txt", "r")
    lastUpdated = datetime.fromisoformat(f.read())
    f.close()
    await scan(lastUpdated, datetime.utcnow())
    #TODO: Scan new channels or servers


# When bot is active, it scan and save the messages every X minutes (I think 24 hours is ok)
# It calls scan method every "LOOP_TIME" minutes to scan messages sent since the same amount of time ago
@tasks.loop(minutes=LOOP_TIME)
async def scanEvery():
    await scanSinceLastUpdate()


# This command scan the history of messages from channels in dictionary called dicChannels.
# This dictionary is defined at the beginning of the script.
# Creates a csv file with the messages and extra information about them.
async def scan(after, before, append=True, limit=None):

    # Save time from last time messages were updated
    f = open("LastUpdated.txt", "w")
    f.write(before.isoformat())
    f.close()

    # Create db and open file to write
    data = pd.DataFrame(columns=['author', 'nickname', 'authorID', 'content', 'time', 'channelName', 'channelID', 'serverName', 'serverID'])
    dataJSON = {}
    dataJSON['messages'] = []

    # Iterate over channels
    for chnID in dicChannels.values():

        chn = bot.get_channel(chnID)
        print("Scanning", chn, "Channel of", chn.guild)

        async for msg in chn.history(limit=limit, before=before, after=after):  # limit=None retrieves every message in the channel

            # if it's a valid message
            if validMessage(msg):

                #CSV
                data = data.append({'content': msg.content,  # Append to database
                                    'time': msg.created_at,
                                    'author': msg.author.name,
                                    'authorID': msg.author.id,
                                    'nickname': msg.author.display_name,
                                    'channelName': chn,
                                    'channelID': '{:d}'.format(chn.id),
                                    'serverName': chn.guild,
                                    'serverID': '{:d}'.format(chn.guild.id)}, ignore_index=True)

                #JSON
                dataJSON['messages'].append({
                    'content': msg.content,  # Append to database
                    'time': msg.created_at,
                    'author': msg.author.name,
                    'authorID': msg.author.id,
                    'nickname': msg.author.display_name,
                    'channelName': chn.name,
                    'channelID': '{:d}'.format(chn.id),
                    'serverName': chn.guild.name,
                    'serverID': '{:d}'.format(chn.guild.id)
                })

    # Close and save

    #CSV
    if append: data.to_csv('Messages.csv', mode='a', header=False)
    else: data.to_csv('Messages.csv', mode='w', header=True)

    #JSON
    # TODO: Find a more efficient way to append data to JSON data file
    if append:
        with open('MessagesJSON.txt') as f:
            loadedData = json.load(f, cls=Encoder.DateTimeDecoder)
        loadedData['messages'].extend(dataJSON['messages'])
        with open('MessagesJSON.txt', 'w') as outfile:
            json.dump(loadedData, outfile, cls=Encoder.DateTimeEncoder)
        processData(dataJSON)

        #with open('MessagesJSON.txt', 'a') as outfile:
        #    json.dump(dataJSON, outfile, cls=Encoder.DateTimeEncoder)
    else:
        with open('MessagesJSON.txt', 'w') as outfile:
            json.dump(dataJSON, outfile, cls=Encoder.DateTimeEncoder)
        processData(dataJSON, True)


# Split words from message and add them individually to the dictionary
def processData(newData, new=False):
    # Update existing dictionary
    if not new:
        with open('dictionary.txt') as d:
            dic = json.load(d)
        with open('dictionaryNames.txt') as d:
            dicNames = json.load(d)
    else:
        dic = {}
        dicNames = {}

    for entry in newData['messages']:

        if entry['authorID'] not in dicNames:
            dicNames[entry['authorID']] = [entry['author'], entry['nickname']]


        for word in str.split(entry['content']):
            if word in dic:  # Word is in the dictionary already
                l = dic[word]  # l is a dictionary
                if entry['authorID'] not in l.keys():  # The user hasn't written that word previously
                    l[entry['authorID']] = 1  # Add user to the dictionary of that word
                else:
                    l[entry['authorID']] += 1

            else:  # Word is not in the dictionary
                dic[word] = {entry['authorID']: 1}

    with open('dictionary.txt', 'w') as outfile:
        json.dump(dic, outfile)
    with open('dictionaryNames.txt', 'w') as outfile:
        json.dump(dicNames, outfile)

    # TODO: Do not count commands or chatbot messages
    # TODO: Group related concepts

def validMessage(msg):

    if msg.type == discord.MessageType.default and not msg.author.bot:
        return True


# ----- Establish connection with server ------ #
bot.run(os.getenv('DISCORD_TOKEN'))

