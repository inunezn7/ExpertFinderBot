# ExpertFinderBot :robot:

Expert finder is a Bot for Discord platform and its aim is to help users to find experts members of the community in certain topic. 
This allows to ask for help about that topic to the right person and to guide the tasks assignation within a team.
The recommendation system is based on term frequency and in the last version make use of Word Embeddings technique to enhance its performance.

For now it is available just in Pharo Discord Community where has been tested.

## How to use it :monocle_face:

As any other Bot in Discord, ExpertFinder needs to use a prefix to execute the available commands. 
In this case the prefix chosen is ``>>`` and the command word to search for experts is simply ``expert``.

For instance, to find an expert in "seaside" (a popular web framework library for Pharo) it is necessary 
to type ``>>expert seaside`` as shown in the following figure:

<p align="center">
  <img src="https://github.com/inunezn7/ExpertFinderBot/blob/master/figures/queryExample.png">
</p>

the answer to the query includes a list of 5 community members considered experts by the Bot, their nicknames, the number of times the user used the concept
and whether the user is online, offline or idle at the moment the query was made.

The command-type message could be sent either in a private message (DM) to the Bot or in a public channel in the server. 
In both cases the Bot replies privately.

## Other commands

:white_check_mark:  ``expertOnline``: It searches for experts whose are online at the moment the query was made. 
Because of the online members it is a reduced number, the precision of the search could be affected.

:bulb:  ``idea``: Give an idea, make a suggestion or write some comments about the project to the Bot's authors.

## How it works

### Baseline

The retrieval system is based on the number of messages the users have sent that contain the concepts entered in the query along their message history.
For multiple-concept queries, the number of messages where all the words on the query have been used are considered to calculate the level of expertise.

### Word Embeddings

The baseline is improved by using a Word Embedding model trained with the message history of the Discord Server. 
This allows to associate terms related by their meaning. For instance, the next table shows the most similar words to "database":

| Concept       | Cosine Similarity   |
| ------------- |:-------------------:|
|"databses"     | 0.74      |
|"db"           | 0.73      |
|"relational"   | 0.71      |
|"nosql"        | 0.71      |
|"postgres"     | 0.71      |
|"migrations"   | 0.7       |
|"dbs"          | 0.69      |

Taking into account that experts generally know about related concepts and topics, it was decided to also count the messages where the expert candidates
use similar words according to the Word Embedding model.

## Preliminar evaluation :bar_chart:

The evaluation made over selected queries by asking people retrieved in the Bot's results whether they are experts or not, 
reveals that ExpertFinder precision is between 0.55 and 0.78 on average, which means more than the half of the members classificated as 
experts for the Bot indeed have certain level of expertise in the topic asked.

It also shows that at least the 88% of the times the first result that the Bot retrieves corresponds to an expert.

## Limitations

The methodology used do not define a threshold to determine whether a user is an expert or not, so it produces a kind of *relative knowledge ranking*.
Therefore it is fair to say that it is not a problem when the list of candadites to experts is large enough, because the Bot's answers take just the top-5 users,
but it leads to imprecise results when there are not too many users using the concepts queried.

# Installation

To install the ExpertFinder it is necessary to download the main folder and link an existing bot to the "main.py" file by creating a .env file with its token. It is also necessary to change some parameters like the Discord's adminID and the Discord community ID where you want the bot works in.

It's is important to add that the Bot needs the permission from one admin of the Discord server where it is going to operate. That can be done in the bot's settings in Discord.

Once the bot was included to the target server, the command ``>>scanFromScratch`` has to be executed by the bot's admin to scan the messages history of the server.

A script to train a Word Embeddings model is provided in the file "WordEmbeddings.py". It can be executed when the bot has already stored the messages history of the server.

# About the authors

This project has being developed by Ignacio Nunez (Nacho#5274 on Discord) and supervised by Alexandre Bergel from University of Chile.
For further information or suggestions feel free to email us to inunezn@fen.uchile.cl.

