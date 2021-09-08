import re
import json
import pandas as pd
from datetime import datetime
import discord

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

# Toma dos listas y arma todos los pares posibles
# Solo segunda lista puede ser vacía
def par(lista1, lista2):
    if len(lista2) == 0: return lista1
    ans = []
    for i in lista1:
        for j in lista2:
            ans.append(i + "_" + j)

    return ans


""" --------------------------------------------------------------------------------------------------------------------

multi_words_same_msg: Multiple concept query searching

It search for experts based on a multiple concept query considering the messages where all the concepts where mentioned.

-------------------------------------------------------------------------------------------------------------------- """


def multi_words_same_msg(Concepts, dicMsgs):
    concepts = []
    # lowerCase concepts:
    for concept in Concepts:
        concepts.append(concept.lower())

    experts = {}

    # Intersections between words mentions
    candidates_byword = dicMsgs[concepts[0]].keys()

    for concept in concepts[1:]:
        candidates_byword = candidates_byword & dicMsgs[concept].keys()

    candidates = {}
    for candidate in candidates_byword:
        msgs_list = set(dicMsgs[concepts[0]][str(candidate)]["msgsID"])

        for concept in concepts[1:]:
            new_list = set(dicMsgs[concept][str(candidate)]["msgsID"])
            msgs_list = msgs_list & new_list

        candidates[candidate] = len(msgs_list)

    return candidates


def updateDic(dic_orig, dic_add, g, max=None):
    dic_new = dic_orig

    for element in dic_add:
        # To avoid take into account deleted members
        memb = g.get_member(int(element))
        if memb is not None:
            if element in dic_new:
                # dic_new[element] += min(dic_add[element], max)
                dic_new[element] += dic_add[element]
            else:
                dic_new[element] = dic_add[element]

    return dic_new


def get_usersList(concept, dic):
    usersList = {}
    for user in dic[concept]:
        usersList[user] = dic[concept][user]["count"]
    return usersList


def comp_word(word):
    words = word.replace("_", " ").split()
    if len(words) == 1:
        return 0
    else:
        return words


# Add to log
# Create db and open file to write
def log(msg, fromBot=False, ctx=None):
    dataLog = pd.DataFrame(
        columns=['author', 'authorID', 'content', 'time', 'channel', 'msgID'])

    if fromBot:

        dataLog = dataLog.append({
            'content': msg,  # Append to database
            'time': datetime.now(),
            'author': 99999,
            'authorID': "ExpertFinder",
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
    global dicMentions
    global dicMsgs
    global dicNames

    # Create new dictionary
    if new:
        dicMentions = {}
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
                    break

                # Keep just letters
                word = cleanWord(word)

                # and it's not a stop word
                if word not in stopwords:

                    for i in range(len(words)):

                        # For multiple-word queries
                        if i + 1 == 1:
                            pass
                        elif i + 1 == 2:
                            word = words[0] + " " + words[1]
                        elif i + 1 == 3:
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
                                    # l[author_id] = 1  # Add user to the dictionary of that word
                                    l[author_id] = {"count": 1, "msgsID": [entry["msgID"]]}
                                else:
                                    # l[author_id] += 1
                                    l[author_id]["count"] += 1
                                    l[author_id]["msgsID"].append(entry["msgID"])

                            # Word is not in the dictionary
                            else:
                                dicMsgs[word] = {author_id: {"count": 1, "msgsID": [entry["msgID"]]}}

                            tempList.append(word)

                        # ------------------------------------------------
                        #              Mentions dictionary
                        # ------------------------------------------------

                        # Word is in the dictionary already
                        if word in dicMentions:
                            l = dicMentions[word]  # reminder: l is a dictionary
                            if author_id not in l.keys():  # The user hasn't written that word previously
                                l[author_id] = 1  # Add user to the dictionary of that word
                            else:
                                l[author_id] += 1

                        # Word is not in the dictionary
                        else:
                            dicMentions[word] = {author_id: 1}

                else:
                    words = []

            else:
                words = []

    # Save dictionaries
    with open('dictionary.txt', 'w') as outfile:
        json.dump(dicMentions, outfile)
    with open('dictionaryMsgs.txt', 'w') as outfile:
        json.dump(dicMsgs, outfile)
    with open('dictionaryNames.txt', 'w') as outfile:
        json.dump(dicNames, outfile)


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

def main():
    pass

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()