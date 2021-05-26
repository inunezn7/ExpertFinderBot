from discord.ext import commands, tasks
import discord
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import timedelta, datetime, timezone
import json
import Encoder
import operator
import re

# ----- Set up ------ #
stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
             "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
             "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these",
             "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
             "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while",
             "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before",
             "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
             "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
             "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
             "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "hello", "hi"]
PREFIX = '>>'
load_dotenv('.env')  # Load TOKEN
intents = discord.Intents(messages=True, members=True, guilds=True, presences=True)
bot = commands.Bot(command_prefix=PREFIX, intents=intents) # Connection to Discord
bot.description = "Hi ! I'm a bot designed to be useful to open " \
                  "source communities by finding expert users in " \
                  "a topic you need some help with. In that way you can mention or send a DM to " \
                  "some of them to deliver your question. " \
                  "My recommendations are based on the messages people have sent in this " \
                  "discord server. " \
                  "\n\n" \
                  "Check my commands below. I hope I can give you a hand! " \
                  "\n\n" \
                  "Developed by Ignacio Nunez (Nacho#5274) and supervised by " \
                  "Alexandre Bergel (Pharo server admin) from University of Chile."



os.chdir("/Users/Nacho/Desktop/ChatBot Project/")   # Project directory
#os.chdir("/home/inunez/ChatBot Project/")   # Project directory
LOOP_TIME = 30  # Minutes between iterations
N_EXPERTS = 6
N_MIN_MENTIONS = 3
SCAN_NUMBER = 1

# ----- Users IDs ------ #
nachoID = 700809908861403286

# ----- Channels IDs ------ #

# Manual definition of channel to scan

dicChannels = {}
# #dicChannels["Nacho_general"] = 700810165447950399
# dicChannels["ISCLab_general"] = 484788823444946965
# dicChannels["ISCLab_pharo"] = 485114368644612097
# dicChannels["ISCLab_vr"] = 689530665531736114
# dicChannels["ISCLab_robotic"] = 485114229083602944
# dicChannels["ISCLab_ia"] = 485114244522704911
# dicChannels["ISCLab_visualization"] = 485114270049239041
# dicChannels["ISCLab_kotlin"] = 485114297374998552

#dicChannels["Pharo_hadoop"] = 494540796414918668

# Enter the ID of the server to scan messages
# Also, it is needed to show the nickname of the user in that Server

ISCLAB_ID = 484788823444946963
Pharo_ID = 223421264751099906 # Pharo Server

GUILD_ID = Pharo_ID

# ----- On_ready event ------ #
@bot.event
async def on_ready():  # on_ready is called when the client is done preparing the data received from Discord
    print("-------------------------------------------------------------------------------------------------------- \n")
    print('We have logged in as {0.user}'.format(bot))  # In response, print something
    print(datetime.now())
    print("\n --------------------------------------------------------------------------------------------------------")
    # for server in bot.guilds:
    #     print("\n", server.name)
    #     print("\n", server.id)
    #     for ch in server.channels:
    #         print(ch)
    #         print(ch.id)

    server = bot.get_guild(GUILD_ID)
    member_count = len([m for m in server.members if not m.bot])
    print(f'Member Count {member_count}')

    for m in server.members:
        if m.bot:
            print(m)

    members_online = len([m for m in server.members if not m.bot and m.status == discord.member.Status.online])
    print(f'Online members {members_online}')

    # To scan every channel on the server

    for ch in server.channels:
        #print(ch.type.name)
        #print(ch.type)
        if ch.type.name == "text" and not ch.id == 361417134997241856: # gsoc_planning
            #print(ch.name)
            dicChannels[ch.name] = ch.id

    scanEvery.start()

# ----- On_message event ------ #
@bot.event
async def on_message(msg):  # It is called when the bot receives a message

    if msg.author == bot.user:  # To check the message was not sent by ourselves.
        return

    elif msg.content.startswith('$hello'):
        await msg.channel.send('Hello!')

    # Make sure the Bot prefix it's at the beginning of the message (In order to not to show a reply
    # every time someone type >>)
    elif msg.content.startswith(PREFIX):

        log(msg) # Add message to log
        await bot.process_commands(msg)  # This line is necessary to allow the bot to hear the commands after
                                         # receive the on_message event.

        if isinstance(msg.channel, discord.DMChannel):

            if msg.content.startswith(PREFIX + " "):

                embedVar = discord.Embed(title="Invalid Command",
                                         description="The command you entered is invalid. Please make sure there is not"
                                                     " a white space between the '>>' and the command name. For "
                                                     "more information type '>>help' command.",
                                         color=0x00ff00)
                await send_nLog(whereTo=msg.author, msgString=embedVar.title + "\n" + embedVar.description, embed=True,
                                msgEmbed=embedVar) # Replies in private

    # Check it's DM
    elif isinstance(msg.channel, discord.DMChannel):

        # Add message to log
        log(msg)

        # Embedded message
        embedVar = discord.Embed(
            title="Hi there!",
            description="Hi ! I'm a bot designed to be useful to open "
                        "source communities by finding expert users in "
                        "a topic you need some help with. In that way you can mention or send a DM to "
                        "some of them to deliver your question. "
                        "My recommendations are based on the messages people have sent in this "
                        "discord server. I hope I can give you a hand!"
                        "\n\n"
                        "To do so, you just need to write my command prefix [>>] next to the word 'expert' "
                        "followed by the concept(s) you want to ask for. For instance if you need help with"
                        " the Roassal library (for visualization in Pharo) you have to send the message "
                        "``>>expert roassal`` and it will retrieve the people who talk about that "
                        "the most. It includes the number of times each user has mentioned that concept "
                        "on the server and whether the person is online or not."
                        "\n\n"
                        "You can also give us a suggestion or an improvement idea with the command "
                        "``>>idea`` followed by your comments. It will be very appreciated!"
                        "\n\n"
                        "For more information please type '>>help'."
                        "\n\n"
                        "I'm being developed by Ignacio Nunez (Nacho#5274) and supervised by "
                        "Alexandre Bergel (Pharo server admin) from University of Chile. "
                        "For further information or suggestions feel free "
                        "to email us to inunezn@fen.uchile.cl",
            color=0x00ff00)

        await send_nLog(whereTo=msg.author, msgString=embedVar.title + "\n" + embedVar.description, embed=True,
                        msgEmbed=embedVar) # Replies in private


@bot.command(name='idea',
             brief='Do you see some improvements? Any suggestions? Please tell me!',
             description='What you would like me to do? Please tell me !',
             help="I would appreciate if you tell me an improvement idea you have, a suggestion or simply what you "
                  "would like a bot could do in order to help the open source communities. "
                  "\n\n"
                  "Please type the command '>>idea' followed by your comments. For example: "
                  "'>>idea Maybe you can show what an user is expert in when his name is entered.'"
                  "\n\n"
                  "Thank you! :)")
async def idea(ctx, *message):

    # Create db and open file to write
    dataIdeas = pd.DataFrame(
        columns=['author', 'authorID', 'content', 'time', 'channel'])

    msg = ""
    for word in message:
        msg = msg + word + ' '

    #CSV
    dataIdeas = dataIdeas.append({
        'content': msg,  # Append to database
        'time': datetime.now(),
        'author': ctx.author,
        'authorID': ctx.author.id,
        'channel': ctx.channel},
        ignore_index=True)

    # CSV
    dataIdeas.to_csv('ideas.csv', mode='a', header=False)

    embedVar = discord.Embed(
        title="Thank you for your comment :D",
        color=0x00ff00)

    await send_nLog(whereTo=ctx.author, msgString=embedVar.title, embed=True, msgEmbed=embedVar) # Replies in private


@bot.command(name='expert',
             brief="Type a key concept and I'll find some experts you can ask about it",
             description="Type a key concept related to some topic you need some help with and I will show you "
                         "people who have mentioned it frequently on this server. In that way you can mention or send "
                         "a DM to some of them to deliver your question."
                         "I hope I can give you a hand!",
             help="To find an expert you just need to write the word 'expert' next to my command prefix [>>] "
                  "followed by the concept(s) you want to ask for. For instance if you need help with"
                  " the Roassal library (for visualization in Pharo) you have to send the message "
                  "'>>expert roassal' and it will retrieve the people who talk about that "
                  "the most. It includes the number of times each user has mentioned that concept "
                  "on the server and whether the person is online or not.")
async def expert(ctx, *concepts):
    await expert_fun(ctx, concepts, False, False)


async def expert_fun(ctx, concepts, online, messages):
    # Define guild
    g = bot.get_guild(GUILD_ID)

    if messages:        # Count messages where the concept was mentioned instead of counting the number of mentions
        with open('dictionaryMsgs.txt') as d:
            dic = json.load(d)
    else:
        # Open concepts dictionary
        with open('dictionary.txt') as d:
            dic = json.load(d)

    with open('dictionaryNames.txt') as d:
        dicNames = json.load(d)

    # All concepts in one
    concept = " ".join(concepts)

    # Change to lowercase
    concept = concept.lower()

    # Check whether the concept it's in the dictionary
    if concept not in dic:
        await send_nLog(whereTo=ctx.author, msgString="So sorry, your concept has not be mentioned in this server",
                        embed=False) # Replies in private
        return

    usersList = dic[concept]
    experts = {}

    for user in usersList:

        # To avoid take into account deleted members
        memb = g.get_member(int(user))
        if memb is not None:

            if online:
                # For expertOnline command
                if memb.status == discord.member.Status.online:
                    experts[user] = usersList[user]

            else:

                experts[user] = usersList[user]


    # Sort experts dictionary
    experts = sorted(experts.items(), key=lambda x: x[1], reverse=True)

    # What's shown in chat Channel
    output = []

    # Join username and nickname
    count = 0
    for e in experts:
        exp = dicNames[e[0]]
        memb = g.get_member(int(e[0]))
        membStatus = memb.status

        if membStatus == discord.member.Status.online:
            emoji = "<:online:816440547299295252>"
        elif membStatus == discord.member.Status.offline:
            emoji = "<:offline:816439965255729173>"
        elif membStatus == discord.member.Status.idle:
            emoji = "<:idle:816439999666847775>"
        else:
            emoji = ""

        count += 1
        if count > N_EXPERTS or e[1] < N_MIN_MENTIONS:
            break

        output.append('{} @{} *({} mentions) {} {}*'.format(exp[1], exp[0], e[1], membStatus, emoji))

    # Notify if no experts were found
    if len(output) == 0:
        if online:
            embedVar = discord.Embed(title="I couldn't find any experts online for " + " ".join(concepts),
                                     color=0x00ff00)
        else:
            embedVar = discord.Embed(title="I couldn't find any experts for " + " ".join(concepts),
                                    color=0x00ff00)
        # Reminder of DM communication
        # if not isinstance(ctx.channel, discord.DMChannel):
        #     embedVar.set_footer(text="* For multiple queries, please consider to make them in private. Just send me a "
        #                              "DM!")
        # Send message and add it to the log
        await send_nLog(whereTo=ctx.author, msgString=embedVar.title, embed=True, msgEmbed=embedVar) # Replies in private

    else:
        embedVar = discord.Embed(title="Experts for " + " ".join(concepts),
                                description="\n".join(output),
                                color=0x00ff00)
        # # Reminder of DM communication
        # if not isinstance(ctx.channel, discord.DMChannel):
        #     embedVar.set_footer(text="* For multiple queries, please consider to make them in private. Just send me a "
        #                              "DM!")
        # Send message and add it to the log
        await send_nLog(whereTo=ctx.author, msgString=embedVar.title + "\n" + embedVar.description, embed=True,
                        msgEmbed=embedVar) # Replies in private
    # okTODO: Handle deleted user. e.g. artificial intelligence
    # okTODO: When searching for two concepts or more, sort the list and extend list of experts


@bot.command(name='expertOnline',
             brief="Find experts who are online now",
             description="Type a key concept related to some topic you need some help with and I will show you "
                         "expert users connected to discord in this moment.",
             help="To find an expert you just need to write the word 'expertOnline' next to my command prefix [>>] "
                  "followed by the concept(s) you want to ask for. For instance if you need help with"
                  " the Roassal library (for visualization in Pharo) you have to send the message "
                  "'>>expert roassal' and it will retrieve the people who talk about that "
                  "the most and are online now. It also includes the number of times each user has mentioned that "
                  "concept on the server.")
async def expertOnline(ctx, *concepts):
    await expert_fun(ctx, concepts, online=True)

# ----------------------------------------------------------------------------------------------------------------------

@bot.command(name='expertMsgs',
             hidden=True)
async def expertMsgs(ctx, *concepts):
    await expert_fun(ctx, concepts, False, True)


# ----------------------------------------------------------------------------------------------------------------------
# De prueba

@bot.command(name='expert2Beta', hidden=True)
async def expert2Beta(ctx, *Concepts):

    # Open concepts dictionary
    with open('messagesJSON.txt') as d:
        msgsData = json.load(d)
    with open('dictionaryNames.txt') as d:
        dicNames = json.load(d)

    concepts = []
    # lowerCase concepts:
    i = 0
    for concept in Concepts:
        concepts.append(concept.lower())

    candidates = {}
    experts = {}
    for msg in msgsData['messages']:

        cont = 0
        contTimes = 0
        contTimes_previuos = 10000
        # Count n of words in the message
        for concept in concepts:

            #if concept in msg['content']:
            #    cont += 1
            #else:
            #    break

            contTimes = 0
            first = True
            for word in reversed(str.split(msg['content'].lower())):

                if notURL(word):

                    if Question(word):
                        break

                    word = cleanWord(word)
                    if word == concept:
                        contTimes += 1
                        if first:
                            cont += 1
                            first = False

            if first == True:
                break

        contTimes_previuos = min(contTimes, contTimes_previuos)

        # If every concepts is in the message
        if cont == len(concepts):
            user = msg['authorID']
            if user in candidates.keys():
                candidates[user] += contTimes_previuos
            else:
                candidates[user] = contTimes_previuos

    for j in range(min(5, len(candidates))):
        e = max(candidates.items(), key=operator.itemgetter(1))[0]
        experts[e] = candidates[e]
        candidates.pop(e)

    # What's shown in chat Channel
    output = []

    # Join username and nickname
    count = 0
    for e in experts.keys():
        exp = dicNames[str(e)]
        #memb = g.get_member(int(e[0]))
        #membStatus = memb.status

        # if membStatus == discord.member.Status.online:
        #     emoji = "<:online:816440547299295252>"
        # elif membStatus == discord.member.Status.offline:
        #     emoji = "<:offline:816439965255729173>"
        # elif membStatus == discord.member.Status.idle:
        #     emoji = "<:idle:816439999666847775>"
        # else:
        #     emoji = ""

        output.append('{} @{} *({} mentions)*'.format(exp[1], exp[0], str(experts[e])))

    # Notify if no experts were found
    if len(experts) == 0:
        embedVar = discord.Embed(title="I couldn't find any experts for " + " ".join(concepts),
                                    color=0x00ff00)
        await send_nLog(whereTo=ctx.author, msgString=embedVar.title, embed=True,
                        msgEmbed=embedVar) # Replies in private

    else:
        embedVar = discord.Embed(title="Experts for " + " ".join(concepts),
                                description="\n".join(output),
                                color=0x00ff00)
        await send_nLog(whereTo=ctx.author, msgString=embedVar.title + "\n" + embedVar.description, embed=True,
                        msgEmbed=embedVar) # Replies in private

# ----------------------------------------------------------------------------------------------------------------------

@bot.command(name='expertFirst',
             hidden=True)
async def expertFirst(ctx, *concepts):
    # Define guild
    g = bot.get_guild(GUILD_ID)

    # Open concepts dictionary
    with open('dictionary.txt') as d:
        dic = json.load(d)
    with open('dictionaryNames.txt') as d:
        dicNames = json.load(d)

    first = True
    for concept in concepts:

        # Change to lowercase
        concept = concept.lower()

        # Check whether the concept it's in the dictionary
        if concept not in dic:
            await send_nLog(whereTo=ctx.channel, msgString="So sorry, your concept has not be mentioned in this server", embed=False)
            return

        usersList = dic[concept]
        count=0
        l = len(usersList)

        if first:
            first = False
            experts2 = {}
            for users in range(l):
                e = max(usersList.items(), key=operator.itemgetter(1))[0]

                # To avoid take into account deleted members
                memb = g.get_member(int(e))
                if memb is not None:
                    # For expertOnline command
                    experts2[e] = usersList[e]

                usersList.pop(e)

        else:
            experts2 = {}
            for users in range(l):
                e = max(usersList.items(), key=operator.itemgetter(1))[0]
                min1 = usersList[e]
                usersList.pop(e)
                if e in experts:
                    min2 = experts[e]
                    minimo = min(min1, min2)
                    experts2[e] = minimo

        experts = experts2

    # Sort experts dictionary
    experts = sorted(experts.items(), key=lambda x: x[1], reverse=True)

    # What's shown in chat Channel
    output = []

    # Join username and nickname
    count = 0
    for e in experts:
        exp = dicNames[e[0]]
        memb = g.get_member(int(e[0]))
        membStatus = memb.status

        if membStatus == discord.member.Status.online:
            emoji = "<:online:816440547299295252>"
        elif membStatus == discord.member.Status.offline:
            emoji = "<:offline:816439965255729173>"
        elif membStatus == discord.member.Status.idle:
            emoji = "<:idle:816439999666847775>"
        else:
            emoji = ""

        output.append('{} @{} *({} mentions) {} {}*'.format(exp[1], exp[0], e[1], membStatus, emoji))
        count += 1
        if count > 5:
            break

    # Notify if no experts were found
    if len(experts) == 0:

        embedVar = discord.Embed(title="I couldn't find any experts for " + " ".join(concepts),
                                    color=0x00ff00)
        await send_nLog(whereTo=ctx.channel, msgString=embedVar.title, embed=True, msgEmbed=embedVar)

    else:
        embedVar = discord.Embed(title="Experts for " + " ".join(concepts),
                                description="\n".join(output),
                                color=0x00ff00)
        await send_nLog(whereTo=ctx.channel, msgString=embedVar.title + "\n" + embedVar.description, embed=True, msgEmbed=embedVar)

# ----------------------------------------------------------------------------------------------------------------------

@bot.command(name='scanFromScratch', help='Scan messages from every Channel from the start of the server until now',
             hidden=True)
async def scanFromScratch(ctx):

    # Check if the user can use the command
    if ctx.author.id != nachoID:
        await send_nLog(whereTo=ctx, msgString="I'm sorry, you are not allowed to use this command :(", embed=False)
        return

    await scan(datetime(2016, 1, 1, 0, 0, 0, 0), datetime.utcnow(), append=False)  # A long time ago year. To scan all the messages from the server
    await send_nLog(whereTo=ctx, msgString="Scan completed", embed=False)


# Command
@bot.command(name='scanCommand', help='Scan messages from every Channel since last time server was scanned',
             hidden=True)
async def scanCommand(ctx):

    # Check if the user can use the command
    if ctx.author.id != nachoID:
        await send_nLog(whereTo=ctx, msgString="I'm sorry, you are not allowed to use this command :(", embed=False)

        return

    await scanSinceLastUpdate()
    await send_nLog(whereTo=ctx, msgString="Scan completed", embed=False)


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

    # Create db and open file to write
    data = pd.DataFrame(columns=['author', 'nickname', 'authorID', 'content', 'time', 'channelName', 'channelID', 'serverName', 'serverID'])
    dataJSON = {}
    dataJSON['messages'] = []

    # Starting
    time_start = datetime.now()
    print("\nStarting scan at " + str(time_start))

    # Iterate over channels
    for chnID in dicChannels.values():

        chn = bot.get_channel(chnID)
        #print("Scanning", chn, "Channel of", chn.guild)

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
        saveLastUpdate(before)
        processData(dataJSON)

    else:
        with open('MessagesJSON.txt', 'w') as outfile:
            json.dump(dataJSON, outfile, cls=Encoder.DateTimeEncoder)
        saveLastUpdate(before) # TODO: Run this line just if the data was successfully written in the file
        processData(dataJSON, True)

    global SCAN_NUMBER
    print("Scan number " + str(SCAN_NUMBER) + " completed successfully in " + str((datetime.now() -
                                                                            time_start).total_seconds()) + " seconds")
    SCAN_NUMBER += 1



@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.errors.CommandNotFound):

        embedVar = discord.Embed(title="Command not found",
                                 description="The command you entered is invalid. Please check you typed it right. For "
                                             "more information type '>>help' command.",
                                 color=0x00ff00)
        await send_nLog(whereTo=ctx.channel, msgString=embedVar.title + "\n" + embedVar.description, embed=True, msgEmbed=embedVar)


# Add to log
# Create db and open file to write
def log(msg, fromBot=False, ctx=None):

    dataLog = pd.DataFrame(
        columns=['author', 'authorID', 'content', 'time', 'channel', 'msgID'])

    if fromBot:

        dataLog = dataLog.append({
            'content': msg,  # Append to database
            'time': datetime.now(),
            'author': bot.user.name,
            'authorID': bot.user.id,
            'channel': ctx,
            'msgID': None
        }, ignore_index=True)

    else:

        dataLog = dataLog.append({
            'content': msg.content,  # Append to database
            'time': datetime.now(),
            'author': msg.author,
            'authorID': msg.author.id,
            'channel': msg.channel,
            'msgID': msg.id
        }, ignore_index=True)

    # CSV
    dataLog.to_csv('log.csv', mode='a', header=False)

async def send_nLog(whereTo, msgString, embed=False, msgEmbed=""):

    if embed:
        log(msg=msgString, fromBot=True, ctx=whereTo)
        await whereTo.send(embed=msgEmbed)
    else:
        log(msg=msgString, fromBot=True, ctx=whereTo)
        await whereTo.send(msgString)


# Split words from message and add them individually to the dictionary
def processData(newData, new=False):

    # Update existing dictionary
    if not new:
        with open('dictionary.txt') as d:
            dic = json.load(d)
        with open('dictionaryMsgs.txt') as d:
            dicMsgs = json.load(d)
        with open('dictionaryNames.txt') as d:
            dicNames = json.load(d)
    # Create new dictionary
    else:
        dic = {}
        dicMsgs = {}
        dicNames = {}

    # Iterate over each entry (message)
    for entry in newData['messages']:

        # Reset temp list -> Useful to count messages
        tempList = []

        # Convert author id to string, because JSON format transform keys into string
        author_id = str(entry['authorID'])

        # Store authors in a dictionary in order to get theirs nickname later
        if author_id not in dicNames:
            dicNames[author_id] = [entry['author'], entry['nickname']]

        # Iterate over each word
        words = []

        for word in reversed(str.split(entry['content'].lower())):

            # Insertar palabra en la lista
            words.insert(0, word)

            # If it's not an URL
            if notURL(word):

                # If it doesn't contain a question tag
                if Question(word):
                    words = []
                    break

                # Keep just letters
                word = cleanWord(word)

                # and it's not a stop word
                if word not in stopwords:

                    for i in range(len(words)):

                        # For multiple-word queries
                        if i+1 == 1:
                            pass
                        elif i+1 == 2:
                            word = words[0] + " " + words[1]
                        elif i+1 == 3:
                            word = words[0] + " " + words[1] + " " + words[2]
                            words = words[0:2]

                        # ------------------------------------------------
                        #              Messages dictionary
                        # ------------------------------------------------

                        # Word is in the dictionary already
                        if word not in tempList:
                            if word in dicMsgs:
                                l = dicMsgs[word]  # reminder: l is a dictionary
                                if author_id not in l.keys():  # The user hasn't written that word previously
                                    l[author_id] = 1  # Add user to the dictionary of that word
                                else:
                                    l[author_id] += 1

                            # Word is not in the dictionary
                            else:
                                dicMsgs[word] = {author_id: 1}

                            tempList.append(word)

                        # ------------------------------------------------
                        #              Mentions dictionary
                        # ------------------------------------------------

                        # Word is in the dictionary already
                        if word in dic:
                            l = dic[word]  # reminder: l is a dictionary
                            if author_id not in l.keys():  # The user hasn't written that word previously
                                l[author_id] = 1  # Add user to the dictionary of that word
                            else:
                                l[author_id] += 1

                        # Word is not in the dictionary
                        else:
                            dic[word] = {author_id: 1}

                else: words = []

            else: words = []


    # Save dictionaries
    with open('dictionary.txt', 'w') as outfile:
        json.dump(dic, outfile)
    with open('dictionaryMsgs.txt', 'w') as outfile:
        json.dump(dicMsgs, outfile)
    with open('dictionaryNames.txt', 'w') as outfile:
        json.dump(dicNames, outfile)

    # TODO: Save Messages data in another file -> How to make kind of repository of scanned files?
    # TODO: Do not count commands or chatbot messages
    # TODO: Group related concepts
    # okTODO: Identify question marks in message
    # okTODO: Identify block concepts
    # TODO: Clean concepts. eg. roassal2 roassal3 just roassal. Maybe keep raw version and add cleaned version?
    # okTODO: identify expert when related concepts are given as input. eg. virtual reality. Maybe two search process
    #       in dictionary and check if the results retrieve the same person
    # TODO: Is it useful to handle users mentions?


def saveLastUpdate(time):
    # Save time from last time messages were updated
    f = open("LastUpdated.txt", "w")
    f.write(time.isoformat())
    f.close()


def validMessage(msg):

    if msg.type == discord.MessageType.default and not msg.author.bot:
        return True


def notURL(word):

    # The word is not a URL direction
    if word[0:8] == "https://" or word[0:7] == "http://":
        return False

    return True


def Question(word):

    # To know if there is a question tag in the message
    for letter in word:
        if letter == '?':
            return True

    return False


def cleanWord(word):

    # From stackoverflow: "'\W' is the same as [^A-Za-z0-9_] plus accented chars from your locale"
    return re.sub('\W', '', word)

# ----- Establish connection with server ------ #
bot.run(os.getenv('DISCORD_TOKEN'))

