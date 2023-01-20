import pandas as pd
import requests
import json
import numpy as np

BASE_URL = 'https://fantasy.premierleague.com/api/bootstrap-static/'
FIXTURES_URL = 'https://fantasy.premierleague.com/api/fixtures/'    
STATUS_URL = 'https://fantasy.premierleague.com/api/event-status/'

PLAYER_COLUMN_NAMES = {
    'web_name': 'name',
    'selected_by_percent': 'selected%',
    'now_cost': 'price',
    'goals_scored': 'goals',
    'goals_conceded': 'GA',
    'clean_sheets': 'Cs',
    'expected_goals': 'xG',
    'expected_assists': 'xA',
    'expected_goal_involvements': 'xGI',
    'expected_goals_conceded': 'xGA',
    'expected_goals_per_90': 'xG/90',
    'saves_per_90': 'Saves/90',
    'expected_assists_per_90': 'xA/90',
    'expected_goal_involvements_per_90': 'xGI/90',
    'expected_goals_conceded_per_90': 'xGA/90',
    'goals_conceded_per_90': 'GA/90',
    'starts_per_90': 'Starts/90',
    'clean_sheets_per_90': 'Cs/90',
    'chance_of_playing_next_round': 'fitness'
    }

class FPL:

    def __init__(self):
        self.fixtures = self.get_fixtures()
        self.team_ids = self.get_team_ids()
        self.player_ids = self.get_player_ids()
        self.latest_gw = self.get_latest_gameweek_no()
        self.teams = self.get_teams()
        self.players = self.get_players()

    def get_team_ids(self):
        
        res = requests.get(BASE_URL)
        data = res.json()
        teams = {}
        for i, j in enumerate(data['teams']):
            teams[i+1] = j['name']

        return teams

    def get_teams(self):
        res  = requests.get(BASE_URL)
        data = res.json()
        return pd.DataFrame(data['teams'])

    def get_players(self):
        
        res = requests.get(BASE_URL)
        data = res.json()
        
        players = pd.DataFrame(data['elements'])
        positions = pd.DataFrame(data['element_types'])
        teams = pd.DataFrame(data['teams'])

        players['position'] = players.element_type.map(positions.set_index('id').singular_name)
        players['form'] = players.form.astype(float)
        players['expected_goals'] = players.expected_goals.astype(float)
        players['expected_assists'] = players.expected_assists.astype(float)
        players['expected_goal_involvements'] = players.expected_goal_involvements.astype(float)
        players['expected_goals_conceded'] = players.expected_goals_conceded.astype(float)
        players['team_name'] = players.team.map(teams.set_index('id').name)
        players['value'] = players.total_points / players.now_cost
        players['ppm'] = players.total_points / players.minutes
        players['now_cost'] /= 10
        players.rename(columns=PLAYER_COLUMN_NAMES, inplace=True)
        modcols = list(PLAYER_COLUMN_NAMES.values())
        
        return players[['id', 'team', 'team_name', 'position',
        'minutes','total_points', 'ppm', 'form', 'value',
        'assists', 'own_goals',
        'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards',
        'saves', 'bonus', 'bps', 'influence', 'creativity', 'threat',
        'ict_index', 'starts'] + modcols]

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

    def get_previous_fixtures(self, team_id, n_gws=5):
        
        fixtures = self.fixtures.loc[(self.fixtures.event >= (self.latest_gw - n_gws)) 
                                        & (self.fixtures.event <= self.latest_gw) 
                                        & ((self.fixtures.team_a == team_id) | (self.fixtures.team_h == team_id))
                                        ,['event', 'team_a', 'team_h', 'team_a_score', 'team_h_score']]
        fixtures['opponent'] = np.where(fixtures.team_a == team_id, fixtures.team_h, fixtures.team_a)
        fixtures['venue'] = np.where(fixtures.team_a == team_id, 'H', 'A')

        return fixtures
    
    def get_upcoming_team_difficulty(self, fixtures, league_table):
        # TODO: Take H/A into account?
        formsum = league_table.query('FPLid in @fixtures.opponent')
        difficulty = formsum.Pts.sum() + formsum.Form.sum()
        return np.divide(difficulty, fixtures.shape[0])

    def get_upcoming_attacking_threat(self, fixtures, league_table):

        df = league_table.query('FPLid in @fixtures.opponent')
        return np.divide(np.divide(df.xG.sum(), df.MP.sum()), fixtures.shape[0])

    def get_upcoming_defensive_difficulty(self, fixtures, league_table):

        df = league_table.query('FPLid in @fixtures.opponent')
        return np.power(np.divide(np.divide(df.xGA.sum(), df.MP.sum()),fixtures.shape[0]), -1)






