from discord.ext import commands, tasks
from cogs.aux_functions import *
import discord
from datetime import datetime
import pandas as pd

class OtherCommands(commands.Cog):

    def __init__(self, bot, adminID):
        self.bot = bot
        self.adminID = adminID

    """ ----------------------------------------------------------------------------------------------------------------

    idea command: It allows an user to give an idea or an opinion about the bot

    ---------------------------------------------------------------------------------------------------------------- """

    @commands.command(name='idea')
    async def idea(self, ctx, *message):
        # Create db and open file to write
        dataIdeas = pd.DataFrame(
            columns=['author', 'authorID', 'content', 'time', 'channel'])

        msg = ""
        for word in message:
            msg = msg + word + ' '

        # CSV
        dataIdeas = dataIdeas.append({
            'content': msg,  # Append to database
            'time': datetime.now(),
            'author': ctx.author,
            'authorID': ctx.author.id,
            'channel': ctx.channel},
            ignore_index=True)

        # CSV
        dataIdeas.to_csv('ideas.csv', mode='a', header=False)

        # Reply
        embedVar = discord.Embed(
            title="Thank you for your comment :D",
            color=0x00ff00)

        await send_nLog(whereTo=ctx.author, msgString=embedVar.title, embed=True,
                        msgEmbed=embedVar)  # Replies in private