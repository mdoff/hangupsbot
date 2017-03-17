from hangups.ui.utils import get_conv_name

from hangupsbot.utils import text_to_segments
from hangupsbot.handlers import StopEventHandling
from hangupsbot.commands import command
import requests
import datetime

class RiotAPI:
    APIKEY = ''
    ENDPOINT = 'https://eune.api.pvp.net'
    GLOBALENPOINT = 'https://global.api.pvp.net'
    REGION = 'eune'
    OBREGION = 'EUN1'
    def __init__(self):
        pass

    def __return(self, url):
        r = requests.get(url)
        return r.json()

    def getPlayerByName(self, name):
        url = self.ENDPOINT + '/api/lol/'+self.REGION+'/v1.4/summoner/by-name/' + name + '?api_key=' + self.APIKEY
        return self.__return(url)

    def getPlayerCurrentGame(self, playerId):
        url = self.ENDPOINT + '/observer-mode/rest/consumer/getSpectatorGameInfo/'+self.OBREGION+'/' + str(playerId) + '/?api_key=' + self.APIKEY
        return self.__return(url)

    def getPlayerLatestGames(self, playerId):
        url = self.ENDPOINT + '/api/lol/'+self.REGION+'/v1.3/game/by-summoner/' + str(playerId) + '/recent?api_key=' + self.APIKEY
        return self.__return(url)

    def getChamionById(self, championId):
        url = self.GLOBALENPOINT + '/api/lol/static-data/'+self.REGION+'/v1.2/champion/' + str(championId) + '?champData=info&api_key=' + self.APIKEY
        return self.__return(url)

def formatTime(timestamp):
    return datetime.datetime.fromtimestamp(
        int(int(timestamp)/1000)
    ).strftime('%Y-%m-%d %H:%M:%S')

def getPlayerInfo(api, player):
    latestsGames = api.getPlayerLatestGames(player['id'])
    latestGame = latestsGames['games'][0]
    champion = api.getChamionById(latestGame['championId'])

    status = 'lost'
    if(latestGame['stats']['win']):
        status = 'won'
    currentGame = api.getPlayerCurrentGame(player['id'])
    currentMsg = '\n' + player['name'] + ' is not playing now'
    if 'gameId' in currentGame:
        if (currentGame['gameStartTime'] < 100):
            currentMsg = '\n' + player['name'] + ' is waiting to load game'
        else:
            currentMsg = '\n' + player['name'] + ' is plaing now since ' + formatTime(currentGame['gameStartTime'])
        currentMsg += ' ( ' + str(currentGame['gameLength']/60) +' minutes ) '
        currentMsg += 'in '+currentGame['gameMode']+' mode'
    readableDate = formatTime(latestGame['createDate'])
    msg = player['name'] + ' played as ' + champion['name'] + ' in ' + latestGame['gameMode'] + ' mode'
    msg += ' at ' + readableDate + ' and ' + status + ' ' + currentMsg
    return msg


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
        msg = "Player not found"
        if (playerName.lower() in player):
            player = player[playerName.lower()]
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
