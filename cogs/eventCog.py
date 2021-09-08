from discord.ext import commands
from cogs.aux_functions import *
import discord
from datetime import datetime
import asyncio

global embedVar
embedVar = discord.Embed(title="Invalid Command",
                         description="The command you entered is invalid. Please make sure there is not"
                                     " a white space between the '>>' and the command name. For "
                                     "more information type '>>help' command.",
                         color=0x00ff00)


class Events(commands.Cog):

    def __init__(self, bot, dicChannels, guild_id, prefix):
        self.bot = bot
        self.dicChannels = dicChannels
        self.GUILD_ID = guild_id
        self.PREFIX = prefix
        self.embedVar = embedVar

    # ----- On_ready event ------ #
    @commands.Cog.listener()
    async def on_ready(self):  # on_ready is called when the client is done preparing the data received from Discord
        print("-------------------------------------------------------------------------------------------------------- \n")
        print('We have logged in as {0.user}'.format(self.bot))  # In response, print something
        print(datetime.now())
        print("\n --------------------------------------------------------------------------------------------------------")

        for g in self.bot.guilds:
            print(g)
            print(g.id)

        server = self.bot.get_guild(self.GUILD_ID)

        # To scan every channel on the server
        for ch in server.channels:
            # add to dicChannels all the text channels the bot has access
            if ch.type.name == "text" and self.bot.user in ch.members:
                # print(ch.name)
                self.dicChannels[ch.name] = ch.id

        # Scan the server periodically
        # scanEvery.start()


    # ----- On_message event ------ #
    @commands.Cog.listener()
    async def on_message(self, msg):  # It is called when the bot receives a message

        if msg.author == self.bot.user:  # To check the message was not sent by ourselves.
            return

        elif msg.content.startswith("hello"):
            await msg.channel.send("Hi")
            return


        # Make sure the Bot prefix it's at the beginning of the message (For not showing a reply
        # every time someone type >>)
        elif msg.content.startswith(self.PREFIX):

            log(msg)  # Add message to log
            #await self.bot.process_commands(msg)  # This line is necessary to allow the bot to hear the commands after
            # receive the on_message event.

            if isinstance(msg.channel, discord.DMChannel):

                if msg.content.startswith(self.PREFIX + " "):
                    # embedVar = discord.Embed(title="Invalid Command",
                    #                          description="The command you entered is invalid. Please make sure there is not"
                    #                                      " a white space between the '>>' and the command name. For "
                    #                                      "more information type '>>help' command.",
                    #                          color=0x00ff00)
                    await send_nLog(whereTo=msg.author, msgString=self.embedVar.title + "\n" + self.embedVar.description, embed=True,
                                    msgEmbed=self.embedVar)  # Replies in private

        # Check whether it is DM
        elif isinstance(msg.channel, discord.DMChannel):

            # Add message to log
            log(msg)

            # Embedded message
            embedVar = discord.Embed(
                title="Hi there!",
                description="I'm a bot designed to find expert users in "
                            "a topic you need some help with. In that way you can mention or send a DM to "
                            "some of them to deliver your question.\n"
                            "I hope I can give you a hand!"
                            "\n\n"
                            "You just need to write the word 'expert' next to my command prefix ``>>`` "
                            "followed by the concept(s) you want to ask for. For instance ``>>expert seaside`` will "
                            "show you a list of experts in seaside library."
                            "\n\n"
                            "**For more information please type ``>>help``.**"
                            "\n\n"
                            "<:github1:859979201108377600> Visit our [GitHub repository](https://github.com/inunezn7/ExpertFinderBot)",
                color=0x00ff00)

            await send_nLog(whereTo=msg.author, msgString=embedVar.title + "\n" + embedVar.description, embed=True,
                            msgEmbed=embedVar)  # Replies in private

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            embedVar = discord.Embed(title="Command not found",
                                     description="The command you entered is invalid. Please check you typed it right. For "
                                                 "more information type '>>help' command.",
                                     color=0x00ff00)
            await send_nLog(whereTo=ctx.channel, msgString=embedVar.title + "\n" + embedVar.description, embed=True,
                            msgEmbed=embedVar)

    @commands.command(name='feedback')
    async def feedback(self, ctx):

        message = await ctx.send("From 1 to 5, how useful for you were the results given by me?")

        await message.add_reaction('1️⃣')
        await message.add_reaction('2️⃣')
        await message.add_reaction('3️⃣')
        await message.add_reaction('4️⃣')
        await message.add_reaction('5️⃣')

        def check(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

        reaction, user = await self.bot.wait_for("reaction_add", check=check)

        await message.delete()
        await ctx.send('Thank you for your feedback!')

"""
    @commands.command(name='feedback2')
    async def feedback2(self, ctx):

        message = await ctx.send('Was my answer useful for you?')

        await message.add_reaction('👍')
        await message.add_reaction('👎')

        def check(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in ['👍', '👎']

        reaction, user = await self.bot.wait_for('reaction_add', check=check)

        await message.delete()
        await ctx.send('Thank you for your feedback!')
"""
