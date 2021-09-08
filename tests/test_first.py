import asyncio
import discord.ext.test as dpytest
import pytest
import os
import discord

#os.chdir("./data")  # Project directory

@pytest.mark.asyncio
async def test_foo(bot):
    await dpytest.message("hello")
    #assert dpytest.verify().message().content("Hi")

    verify = dpytest.VerifyMessage()
    verify.contains()
    verify.content("H")

    assert verify
"""
@pytest.mark.asyncio
async def test_foo2(bot):
    embedVar = discord.Embed(title="Invalid Command",
                             description="The command you entered is invalid. Please make sure there is not"
                                         " a white space between the '>>' and the command name. For "
                                         "more information type '>>help' command.",
                             color=0x00ff00)

    #await dpytest.message(">> hola")
    #msg = await bot.get_user(int(bot.user.id)).send(">> hola")
    print(bot.get_user(int(bot.user.id)).dm_channel)
    ch = await bot.get_user(int(bot.user.id)).create_dm()
    await dpytest.message(">> hola", ch)

    verObj = dpytest.verify().message()
    #verObj.contains()
    verObj.embed(embedVar)

    assert verObj

@pytest.mark.asyncio
async def test_foo3(bot):
    embedVar = discord.Embed(
        title="Hi there!",
        description="I'm a bot designed to find expert users in "
                    "a topic you need some help with. In that way you can mention or send a DM to "
                    "some of them to deliver your question.\n"
                    "I hope I can give you a hand!"
                    "\n\n"
                    "**For more information please type ``>>help``.**"
                    "\n\n"
                    "<:github1:859979201108377600> Visit our [GitHub repository](https://github.com/inunezn7/ExpertFinderBot)",
        color=0x00ff00)

    ch = await bot.get_user(int(bot.user.id)).create_dm()
    await dpytest.message("hola", ch)

    verObj = dpytest.verify().message()
    #verObj.contains()
    verObj.embed(embedVar)

    assert verObj
"""

@pytest.mark.asyncio
async def test_foo4(bot):
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

    ch = await bot.get_user(int(bot.user.id)).create_dm()
    await dpytest.message("hi?", ch)

    verObj = dpytest.verify().message()
    #verObj.contains()
    verObj.embed(embedVar)

    assert verObj