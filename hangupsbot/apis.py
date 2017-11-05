import requests
import datetime

class RiotAPI:
    APIKEY = ''
    ENDPOINT = 'api.riotgames.com'
    REGION = 'eun1'
    def __init__(self):
        pass

    def __return(self, url):
        r = requests.get('https://' + self.REGION + '.' + self.ENDPOINT + url)
        return r.json()
    def __endpoint(self):
      return 'https://' + self.REGION + '.' + self.ENDPOINT
    def getPlayerByName(self, name):
        url = '/lol/summoner/v3/summoners/by-name/' + name + '?api_key=' + self.APIKEY
        return self.__return(url)

    def getPlayerCurrentGame(self, playerId):
        url = '/lol/spectator/v3/active-games/by-summoner/' + str(playerId) + '?api_key=' + self.APIKEY
        return self.__return(url)

    def getPlayerLatestGames(self, playerId):
        url = '/lol/match/v3/matchlists/by-account/' + str(playerId) + '/recent?api_key=' + self.APIKEY
        return self.__return(url)
    
    def getGameDetails(self, gameId):
      url = '/lol/match/v3/matches/' + str(gameId) + '?api_key=' + self.APIKEY
      return self.__return(url)

    def getChamionById(self, championId):
      url = '/lol/static-data/v3/champions/' + str(championId) + '?api_key=' + self.APIKEY
      return self.__return(url)
    

def formatTime(timestamp):
    return datetime.datetime.fromtimestamp(
        int(int(timestamp)/1000)
    ).strftime('%Y-%m-%d %H:%M:%S')

def getPlayerGameDetails(player, game):
  accountId = player['accountId']
  participantIdentity = list(filter(lambda x:
    x['player']['currentAccountId'] == accountId, game['participantIdentities']
  ))[0]
  return list(filter(lambda p: 
    p['participantId'] == participantIdentity['participantId'],game['participants']
  ))[0]

def getPlayerInfo(api, player):
    latestsGames = api.getPlayerLatestGames(player['accountId'])
    games = latestsGames['matches']
    latestGames = api.getPlayerLatestGames(player['accountId'])
    latestGame = api.getGameDetails(latestGames['matches'][0]['gameId'])
    gameInfo = getPlayerGameDetails(player, latestGame)
    status = 'lost'
    if gameInfo['stats']['win']:
      status = 'won'
    # champion = api.getChamionById(games[0]['champion']) # API call limit
    # currentGame = api.getPlayerCurrentGame(player['accountId'])
    
    # currentMsg = '\n' + player['name'] + ' is not playing now'
    # if 'gameId' in currentGame:
    #     if (currentGame['gameStartTime'] < 100):
    #         currentMsg = '\n' + player['name'] + ' is waiting to load game'
    #     else:
    #         currentMsg = '\n' + player['name'] + ' is plaing now since ' + formatTime(currentGame['gameStartTime'])
    #     currentMsg += ' ( ' + str(currentGame['gameLength']/60) +' minutes ) '
    #     currentMsg += 'in '+currentGame['gameMode']+' mode'
    readableDate = formatTime(latestGame['gameCreation'])
    msg = player['name'] + ' ' + status + ' ' + latestGame['gameMode'] + ' game'
    msg += ' at ' + readableDate
    return msg