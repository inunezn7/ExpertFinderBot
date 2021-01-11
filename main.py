import discord
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv('.env')

client = discord.Client()  # The client is the connection to Discord
os.chdir("/Users/Nacho/Desktop/ChatBot Project/")

data = pd.DataFrame(columns=['content', 'time', 'author'])


@client.event
async def on_ready():  # on_ready is called when the client is done preparing the data received from Discord
    print('We have logged in as {0.user}'.format(client))  # In response, print something


@client.event
async def on_message(message):  # It is called when the bot receives a message
    if message.author == client.user:  # To check the message was not sent by ourselves.
        return

    elif message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        await message.channel.send(len(client.guilds))
        members = '\n - '.join([member.name for member in client.guilds[0].members])
        print(f'Guild Members:\n - {members}')

    elif message.content.startswith('scan'):
        f = open("MessagesFromServer.txt", "w")
        async for message in message.channel.history(limit=200):
            f.write(message.content + "\n")
        f.close()
        await message.channel.send("Scan completed")


client.run(os.getenv('DISCORD_TOKEN'))
