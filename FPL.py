import pandas as pd
import requests
import json
import numpy as np

BASE_URL = 'https://fantasy.premierleague.com/api/bootstrap-static/'
FIXTURES_URL = 'https://fantasy.premierleague.com/api/fixtures/'    
STATUS_URL = 'https://fantasy.premierleague.com/api/event-status/'

class FPL:



    def __init__(self):
        self.fixtures = self.get_fixtures()
        self.team_ids = self.get_team_ids()
        self.player_ids = self.get_player_ids()
        self.latest_gw = self.get_latest_gameweek_no()

    def get_team_ids(self):
        
        res = requests.get(BASE_URL)
        data = res.json()
        teams = {}
        for i, j in enumerate(data['teams']):
            teams[i+1] = j['name']

        return teams

    def get_player_ids(self):

        res = requests.get(BASE_URL)
        data = res.json()
        players = {}
        for i, j in enumerate(data['elements']):
            players[i+1] = j['web_name']

        return players
        
    def get_fixtures(self, future_only = False):

        url = FIXTURES_URL
        if future_only:
            url += '?future=1'
        res = requests.get(url)
        data = res.json() 

        return pd.DataFrame.from_records(data, index='code')

    def get_latest_gameweek_no(self):
        
        res = requests.get(STATUS_URL)
        data = res.json()
        

        try:
             return data['status'][0]['event']
        except:
            return None

    def get_upcoming_fixtures(self, team_id, n_gws = 5):

        fixtures = self.fixtures.loc[(self.fixtures.event <= (self.latest_gw + n_gws)) 
                                        & (self.fixtures.event > self.latest_gw) 
                                        & ((self.fixtures.team_a == team_id) | (self.fixtures.team_h == team_id))
                                        ,['event', 'team_a', 'team_h']]
        fixtures['opponent'] = np.where(fixtures.team_a == team_id, fixtures.team_h, fixtures.team_a)
        fixtures['venue'] = np.where(fixtures.team_a == team_id, 'H', 'A')
        fixtures.drop(['team_h', 'team_a'], axis=1, inplace=True)

        return fixtures


fpl = FPL()

x = fpl.get_latest_gameweek_no()
print(x)

df = fpl.get_upcoming_fixtures(1)
print(df.head())













