from discord.ext import commands
from cogs.aux_functions import *
import discord
import numpy as np
import asyncio
from datetime import datetime


class Expert(commands.Cog):

    def __init__(self, bot, adminID, dicMsgs, dicMentions, dicNames, pharo_w2v, guild_id, sim_coef, n_experts, n_min_mentions):
        self.bot = bot
        self.adminID = adminID
        self.dicMsgs = dicMsgs
        self.dicMentions = dicMentions
        self.dicNames = dicNames
        self.pharo_w2v = pharo_w2v
        self.GUILD_ID = guild_id
        self.SIM_COEF = sim_coef
        self.N_EXPERTS = n_experts
        self.N_MIN_MENTIONS = n_min_mentions

    """ ----------------------------------------------------------------------------------------------------------------

    expert command: The default specification of the expert command. It is needed to set the parameters of expert_fun

    ---------------------------------------------------------------------------------------------------------------- """

    @commands.command(name='expert',
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
    async def expert(self, ctx, *concepts):
        await self.expert_fun(ctx, concepts, online=False, messages=True, we=True, weMulti=True, same_message=True)

    """ ----------------------------------------------------------------------------------------------------------------

    expert_fun : The core of expert searching

    ---------------------------------------------------------------------------------------------------------------- """

    async def expert_fun(self, ctx, concepts, online, messages, we=False, weMulti=False, same_message=True):
        # Define guild
        g = self.bot.get_guild(self.GUILD_ID)

        # Lower case
        concepts = [concept.lower() for concept in concepts]

        # Count number of messages or mentions with the concept entered by the user
        if messages:
            dic = self.dicMsgs
        else:
            dic = self.dicMentions

        # All concepts in one
        concept = " ".join(concepts)
        concept_under = "_".join(concepts)

        # Change to lowercase
        concept = concept.lower()

        # Check whether the concept it's in the dictionary or not
        #if concept not in dic:
        #    await send_nLog(whereTo=ctx.author, msgString="So sorry, your concept has not be mentioned in this server",
        #                    embed=False)  # Replies in private
        #    return

        # Find users that have used all the concepts in a multiple-concept query in a same message
        if len(concepts) > 1 and same_message:
            usersList = multi_words_same_msg(concepts, dic)
        else:
            usersList = get_usersList(concept, dic)

        # Initialize the experts list (dictionary)
        experts = {}

        # Add candidates to expert list. It makes sure members accounts are not deleted.
        # If online member option is selected, then just online users are added to the list
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

        # Mix word embedding experts with concept experts
        # Word Embeddings
        if we:

            max = 0
            for element in usersList:
                if usersList[element] > max:
                    max = usersList[element]

            if len(concepts) > 1:

                # Word Embeddings with multiple-words concept
                if weMulti:

                    similar = {}
                    first = 1
                    for concept in concepts:
                        similar[concept] = [sim[0] for sim in
                                            self.pharo_w2v.wv.most_similar(positive=[concept], topn=30) if
                                            sim[0] not in concepts and sim[0] != concept_under and sim[
                                                1] > self.SIM_COEF]

                    print(similar)

                terms = []
                for concept in concepts:
                    terms = par(similar[concept], terms)

                for sword in terms:

                    try:
                        experts = updateDic(experts, multi_words_same_msg(comp_word(sword), dic),
                                            self.bot.get_guild(self.GUILD_ID))
                    except:
                        pass

            else:
                try:
                    similar = self.pharo_w2v.wv.most_similar(positive=[concept], topn=30)
                except:
                    similar = []

                count = 0
                for sword in similar:
                    print(sword)
                    if sword[1] < self.SIM_COEF or count > 10:
                        break
                    try:
                        if same_message and comp_word(sword[0]) != 0:
                            experts = updateDic(experts, multi_words_same_msg(comp_word(sword[0]), dic), self.bot.get_guild(self.GUILD_ID))
                        else:
                            experts = updateDic(experts, get_usersList(sword[0], dic), self.bot.get_guild(self.GUILD_ID))
                    except:
                        pass
                    count += 1

        # Sort experts dictionary
        experts = sorted(experts.items(), key=lambda x: x[1], reverse=True)

        # What's shown in chat Channel
        output = []

        # Join username and nickname
        count = 0
        for e in experts:
            exp = self.dicNames[e[0]]
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
            if count > self.N_EXPERTS or e[1] < self.N_MIN_MENTIONS:
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

            # Send message and add it to the log
            await send_nLog(whereTo=ctx.author, msgString=embedVar.title, embed=True,
                            msgEmbed=embedVar)  # Replies in private

        else:
            embedVar = discord.Embed(title="Experts for " + " ".join(concepts),
                                     description="\n".join(output),
                                     color=0x00ff00)

            # Send message and add it to the log
            await send_nLog(whereTo=ctx.author, msgString=embedVar.title + "\n" + embedVar.description, embed=True,
                            msgEmbed=embedVar)  # Replies in private

    """ ----------------------------------------------------------------------------------------------------------------

    expert_feedback

    ---------------------------------------------------------------------------------------------------------------- """

    async def feedback2(self, ctx):

        message = await ctx.send('Was my answer useful for you?')

        await message.add_reaction('👍')
        await message.add_reaction('👎')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['👍', '👎']

        reaction, user = await self.bot.wait_for('reaction_add', check=check)

        await message.delete()
        await ctx.send('Thank you for your feedback!')


    @commands.command(name='expertFB', hidden=True)
    async def expertFB(self, ctx, *concepts):
        await self.expert_fun(ctx, concepts, False, messages=True, we=True, weMulti=True)
        await asyncio.sleep(10)

        channel = self.bot.get_channel(ctx.channel.id)
        last_msg = await channel.history(limit=1).flatten()
        t0 = last_msg[0].created_at
        t1 = datetime.utcnow()
        delta = t1-t0

        if delta.seconds > 9.9:
            await self.feedback2(ctx)


    """ ----------------------------------------------------------------------------------------------------------------

    expertOnline : Search for expert who are online at the moment of the query 

    ---------------------------------------------------------------------------------------------------------------- """

    @commands.command(name='expertOnline',
                 brief="Find experts who are online now",
                 description="Type a key concept related to some topic you need some help with and I will show you "
                             "expert users connected to discord in this moment.",
                 help="To find an expert you just need to write the word 'expertOnline' next to my command prefix [>>] "
                      "followed by the concept(s) you want to ask for. For instance if you need help with"
                      " the Roassal library (for visualization in Pharo) you have to send the message "
                      "'>>expert roassal' and it will retrieve the people who talk about that "
                      "the most and are online now. It also includes the number of times each user has mentioned that "
                      "concept on the server.")
    async def expertOnline(self, ctx, *concepts):
        await self.expert_fun(ctx, concepts, online=True, messages=True)

    """ --------------------------------------------------------------------------------------------------------------------

    Hidden expert search variations

    -------------------------------------------------------------------------------------------------------------------- """

    @commands.command(name='expertMsgs',
                 hidden=True)
    async def expertMsgs(self, ctx, *concepts):
        await self.expert_fun(ctx, concepts, False, True)

    # ----------------------------------------------------------------------------------------------------------------------

    @commands.command(name='expertWE',
                 hidden=True)
    async def expertWE(self, ctx, *concepts):
        await self.expert_fun(ctx, concepts, False, True, we=True)

    # ----------------------------------------------------------------------------------------------------------------------

    @commands.command(name='expertWEMentions',
                 hidden=True)
    async def expertWEMentions(self, ctx, *concepts):
        await self.expert_fun(ctx, concepts, False, False, we=True)