from hangups.ui.utils import get_conv_name

from hangupsbot.utils import text_to_segments
from hangupsbot.handlers import StopEventHandling
from hangupsbot.commands import command
import requests
import datetime

from hangupsbot.apis import RiotAPI, getPlayerInfo, getPlayerGameDetails

@command.register(alias=True)
def lol(bot, event, *args):
    """Command to fetching data from RiotAPI,
    usage:
    /lol <username>
    /lol list
    /lol add <username>
    /lol remove <username>
    """
    api =  RiotAPI()
    apiKey = bot.config.get_by_path(['lol_api_key'])
    if apiKey is None:
        yield from event.conv.send_message(text_to_segments('API key is not defined'))
        raise StopEventHandling
    if len(args) == 0:
        yield from event.conv.send_message(text_to_segments('username / command not specified'))
        raise StopEventHandling
    api.APIKEY = apiKey

    playerName = args[0]
    #ugly if!
    if (playerName == 'list'):
        yield from list(bot, event, api, *args[1:])
    elif (playerName == 'add'):
        yield from addLol(bot, event, api, *args[1:])
    elif (playerName == 'remove'):
        yield from removeLol(bot, event, *args[1:])
    else:
        player = api.getPlayerByName(playerName)
        msg = "Player not found" + str(player)
        
        if (playerName.lower() == player['name'].lower()):
            msg = getPlayerInfo(api, player)
        yield from event.conv.send_message(text_to_segments(msg))


def list(bot, event, api, *args):
    players = bot.get_config_suboption(event.conv_id, "lol_players")
    res = ''
    for player in players:
        res += getPlayerInfo(api, player) +'\n'
    yield from event.conv.send_message(text_to_segments(res))

def addLol(bot, event, api, *args):
    playerName = args[0]
    player = api.getPlayerByName(playerName)
    msg = "Player not found"
    if (playerName.lower() in player):
        player = player[playerName.lower()]
        players = bot.get_config_suboption(event.conv_id, "lol_players")
        if players is None:
            players = []
        bot.config.set_by_path(["conversations", event.conv_id, "lol_players"], players + [player])
        bot.config.changed = True
        bot.config.save()
        msg = player['name'] + " on " + str(player['summonerLevel']) + " level was added"

    yield from event.conv.send_message(text_to_segments(msg))

def removeLol(bot, event, *args):
    if (len(args) != 1):
        yield from event.conv.send_message(text_to_segments("One player name required"))
        raise StopEventHandling
    playerName = args[0]
    players = bot.get_config_suboption(event.conv_id, "lol_players")
    delta = len(players)
    for p in players:
        if(p['name'].lower() == playerName.lower()):
            players.remove(p)
    bot.config.set_by_path(["conversations", event.conv_id, "lol_players"], players)
    delta = delta - len(players)
    msg = "Player not found"
    if(delta == 1):
        msg = "Player " + playerName + " removed"
        bot.config.changed = True
    elif(delta > 1):
        msg = delta + " players removed"
        bot.config.changed = True
        
    bot.config.save()

    yield from event.conv.send_message(text_to_segments(msg))
