from discord.ext import commands, tasks
from cogs.aux_functions import *
from datetime import datetime
import json
import pandas as pd
from Encoder import *
import os

LOOP_TIME = 720

class Scan(commands.Cog):

    def __init__(self, bot, adminID):
        self.bot = bot
        self.adminID = adminID

    """ --------------------------------------------------------------------------------------------------------------------

    scanFromScratch : It reset the messages history form the database and it is scanned from scratch 

    -------------------------------------------------------------------------------------------------------------------- """

    @commands.command(name='scanFromScratch', help='Scan messages from every Channel from the start of the server until now',
                 hidden=True)
    async def scanFromScratch(self, ctx):
        # Check if the user can use the command
        if ctx.author.id != self.adminID:
            await send_nLog(whereTo=ctx, msgString="I'm sorry, you are not allowed to use this command :(", embed=False)
            return

        await self.scan(datetime(2016, 1, 1, 0, 0, 0, 0), datetime.utcnow(),
                   append=False)  # A long time ago year. To scan all the messages from the server
        await send_nLog(whereTo=ctx, msgString="Scan completed", embed=False)

    """ --------------------------------------------------------------------------------------------------------------------

    scanCommand : This command it is used to scan the messages since the last time it was done 

    -------------------------------------------------------------------------------------------------------------------- """

    @commands.command(name='scanCommand', help='Scan messages from every Channel since last time server was scanned',
                 hidden=True)
    async def scanCommand(self, ctx):
        # Check if the user can use the command
        if ctx.author.id != self.adminID:
            await send_nLog(whereTo=ctx, msgString="I'm sorry, you are not allowed to use this command :(", embed=False)
            return

        await self.scanSinceLastUpdate()
        await send_nLog(whereTo=ctx, msgString="Scan completed", embed=False)

    """ --------------------------------------------------------------------------------------------------------------------

    scanSinceLastUpdate : This is the function to scan the messages since the last time it was done.

    Both the automatic scan and the scan command use this function 

    -------------------------------------------------------------------------------------------------------------------- """

    async def scanSinceLastUpdate(self):

        if not os.path.isfile("LastUpdated.txt"):
            print("LastUpdated not found. It will be created once the scan has finished.")
            await self.scanFromScratch()

        else:
            f = open("LastUpdated.txt", "r")
            lastUpdated = datetime.fromisoformat(f.read())
            f.close()
            await self.scan(lastUpdated, datetime.utcnow())

    # When bot is active, it scan and save the messages every X minutes (I think 24 hours is ok)
    # It calls scan method every "LOOP_TIME" minutes to scan messages sent since the same amount of time ago
    @tasks.loop(minutes=LOOP_TIME)
    async def scanEvery(self):
        await self.scanSinceLastUpdate()

    # This command scan the history of messages from channels in dictionary called dicChannels.
    # This dictionary is defined at the beginning of the script.
    # Creates a csv file with the messages and extra information about them.
    async def scan(self, after, before, append=True, limit=None):
        # Create db and open file to write
        data = pd.DataFrame(
            columns=['author', 'nickname', 'authorID', 'content', 'time', 'channelName', 'channelID', 'serverName',
                     'serverID'])
        dataJSON = {}
        dataJSON['messages'] = []

        # Starting
        time_start = datetime.now()
        print("\nStarting scan at " + str(time_start))

        # Iterate over channels
        for chnID in self.dicChannels.values():

            chn = self.bot.get_channel(chnID)
            # print("Scanning", chn, "Channel of", chn.guild)

            async for msg in chn.history(limit=limit, before=before,
                                         after=after):  # limit=None retrieves every message in the channel

                # if it's a valid message
                if validMessage(msg):
                    # CSV
                    data = data.append({'content': msg.content,  # Append to database
                                        'time': msg.created_at,
                                        'author': msg.author.name,
                                        'authorID': msg.author.id,
                                        'nickname': msg.author.display_name,
                                        'channelName': chn,
                                        'channelID': '{:d}'.format(chn.id),
                                        'serverName': chn.guild,
                                        'serverID': '{:d}'.format(chn.guild.id)}, ignore_index=True)

                    # JSON
                    dataJSON['messages'].append({
                        'content': msg.content,  # Append to database
                        'time': msg.created_at,
                        'author': msg.author.name,
                        'authorID': msg.author.id,
                        'nickname': msg.author.display_name,
                        'channelName': chn.name,
                        'channelID': '{:d}'.format(chn.id),
                        'serverName': chn.guild.name,
                        'serverID': '{:d}'.format(chn.guild.id),
                        'msgID': '{:d}'.format(msg.id)
                    })

        # Close and save

        # CSV
        if append:
            data.to_csv('Messages.csv', mode='a', header=False)
        else:
            data.to_csv('Messages.csv', mode='w', header=True)

        # JSON
        # TODO: Find a more efficient way to append data to JSON data file
        if append:
            with open('MessagesJSON.txt') as f:
                loadedData = json.load(f, cls=DateTimeDecoder)
            loadedData['messages'].extend(dataJSON['messages'])
            with open('MessagesJSON.txt', 'w') as outfile:
                json.dump(loadedData, outfile, cls=DateTimeEncoder)
            saveLastUpdate(before)
            processData(dataJSON)

        else:
            with open('MessagesJSON.txt', 'w') as outfile:
                json.dump(dataJSON, outfile, cls=DateTimeEncoder)
            saveLastUpdate(before)  # TODO: Run this line just if the data was successfully written in the file
            processData(dataJSON, True)

        global SCAN_NUMBER
        print("Scan number " + str(SCAN_NUMBER) + " completed successfully in " + str((datetime.now() -
                                                                                       time_start).total_seconds()) + " seconds")
        SCAN_NUMBER += 1