from discord.ext import commands
from cogs.aux_functions import *
import discord

class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot, prefix):
        self.bot = bot
        self.prefix = prefix

    @commands.command()
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):

        """Shows all modules of that bot"""

        # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        #version =  # enter version of your code

        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:

            # starting to build embed
            emb = helpCommand()

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:
            print(input[0])

            # iterating trough cogs
            #for cog in self.bot.cogs:

            # getting commands from cog
            #for command in self.bot.get_cog(cog).get_commands():
            for command in self.bot.commands:
                # if cog is not hidden
                print(command.name)
                if command.name in dicHelp.keys() and command.name == input[0]:
                    emb = dicHelp[input[0]]
                    break

            # found cog - breaking loop
            #break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="Command not found",
                                    description="The command you entered is invalid. Please check you typed it right. "
                                                     "To check the valid commands, please type '>>help'.",
                                    color=0x00ff00)

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="More than one command entered",
                                description="Please request only one command at once.",
                                color=0x00ff00)

        # sending reply embed using our own function defined above
        await send_nLog(whereTo=ctx.author, msgString=emb.title, embed=True, msgEmbed=emb)  # Replies in private

# ----------------------------------------------------------------------------------------------------------------------

def helpCommand():

    em = discord.Embed(title="Help",
                       description="Use >>help <command> for extended information of one of the following commands:")
    em.add_field(name=":mag: expert",
                 value="Search for experts in a topic you need some help with.\nUsage example: ``>>expert python``.",
                 inline=False)

    em.add_field(name="<:online:816440547299295252> expertOnline",
                 value="Search for experts online at the moment of the query.\nUsage example: "
                       "``>>expertOnline python``.", inline=False)

    em.add_field(name=":bulb: idea",
                 value="Do you see some improvements? Any suggestions? Please tell me!\nUsage example: ``>>idea Maybe "
                       "the bot can also give a brief definition of the topic asked``.", inline=False)

    em.add_field(name = chr(173), value = chr(173), inline=False)

    em.add_field(name="\n:information_source: About",
                 value="Type ``>>help about`` to know more about this project.", inline=True)

    em.add_field(name="<:github1:859979201108377600> Github",
                 value="Visit our "
                       "[GitHub repository](https://github.com/inunezn7/ExpertFinderBot).",
                 inline=True)

    return em

# ----------------------------------------------------------------------------------------------------------------------

def expertHelp():

    em = discord.Embed(title=":mag: expert", description="")

    em.add_field(name="Description",
                 value="Type a key concept related to some topic you need some help with and I will show you "
                       "people who have mentioned it frequently on this server. In that way you can mention or send "
                       "a DM to some of them to deliver your questions.\n"
                       "The results include the number of messages each user has sent mentioning that or other topics "
                       "related on the server and whether the person is online or not.\n"
                       "I hope I can give you a hand!")

    em.add_field(name="Syntax",
                 value="``>>expert [topic]`` where [topic] can be one or more words related to the "
                                      "topic you want to find experts in.",
                 inline=False)

    em.add_field(name="Example",
                 value="For instance, you can type ``>>expert seaside`` in case you want to ask "
                                       "for experts in seaside Pharo library.",
                 inline=False)

    return em

# ----------------------------------------------------------------------------------------------------------------------

def expertOnlineHelp():
    em = discord.Embed(title="<:online:816440547299295252> expertOnline", description="")

    em.add_field(name="Description",
                 value="This command is similar to ``expert`` but just show users online at the moment of the query.",
                 inline=False)

    em.add_field(name="Syntax",
                 value="``>>expertOnline [topic]`` \n where [topic] can be one or more words related to the "
                                      "topic you want to find experts in.",
                 inline=False)

    em.add_field(name="Example",
                 value="For instance, you can type ``>>expertOnline seaside`` in case you want to ask "
                                       "for experts in seaside Pharo library.",
                 inline=False)

    return em

# ----------------------------------------------------------------------------------------------------------------------

def ideaHelp():

    em = discord.Embed(title=":bulb: idea", description="")
    em.add_field(name="Description",
                 value="I would appreciate if you tell me an improvement idea you have, a suggestion or simply what "
                       "you would like a bot could do in order to help the open source communities.\n"
                       "Thank you! :smiley",
                 inline=False)

    em.add_field(name="Syntax",
                 value="Type the command ``>>idea [text]`` where [text] corresponds to your"
                       "comments or suggestions.",
                 inline=False)

    em.add_field(name="Example",
                 value="Let's suppose one person instead of getting a list of experts in one topic, "
                                       "would want to know the expertise fields of one member:"
                                       "``>>idea I would like that the bot can show me what an user is expert in``.",
                 inline=False)

    return em

# ----------------------------------------------------------------------------------------------------------------------

def aboutHelp():

    em = discord.Embed(title="about", description="")
    em.add_field(name="Purpose",
                 value="This bot is an attempt to help open source communities to find experts easily. This could allow"
                       "beginners to know to whom they should direct their questions and also help work teams to assign"
                       "each task to the right person.", inline=False)
    em.add_field(name="Authors",
                 value="The bot is being developed by Ignacio Nunez (Nacho#5274) and "
                        "Alexandre Bergel (Pharo server admin) from University of Chile. "
                        "For further information or suggestions feel free "
                        "to email us to inunezn@fen.uchile.cl", inline=False)
    em.add_field(name="<:github1:859979201108377600> Github",
                 value="Visit our [GitHub repository](https://github.com/inunezn7/ExpertFinderBot).",
                 inline=False)

# ----------------------------------------------------------------------------------------------------------------------
# Dictionary help

dicHelp = {"expert": expertHelp(),
           "expertOnline": expertOnlineHelp(),
           "idea": ideaHelp(),
           "about": aboutHelp()}