import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import time

TEAM_NAME_CONVERSION = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "Bournemouth",
    "Brentford": "Brentford",
    "Brighton and Hove Albion": "Brighton",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Leeds United": "Leeds",
    "Leicester City": "Leicester",
    "Liverpool": "Liverpool",
    "Manchester City": "Man City",
    "Manchester United": "Man Utd",
    "Newcastle United": "Newcastle",
    "Nottingham Forest": "Nott'm Forest",
    "Southampton": "Southampton",
    "Tottenham Hotspur": "Spurs",
    "West Ham United": "West Ham",
    "Wolverhampton Wanderers": "Wolves"
}

def fbref_to_fpl(name):
    try:
        return TEAM_NAME_CONVERSION[name]
    except KeyError:
        return name

def parse_team_name(url):
    team = (' ').join(url.split('/')[-1].split('-')[:-1]).replace('-', ' ')
    return team

def get_team_urls():
    standing_url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    data = requests.get(standing_url)
    soup = BeautifulSoup(data.text, features='lxml')
    standing_table = soup.select('table.stats_table')[0]
    
    links  = standing_table.find_all('a')
    links = [l.get('href') for l in links]
    links = [l for l in links if '/squads/' in l]
    
    team_urls = [f'https://fbref.com{l}' for l in links]
    team_names = [parse_team_name(url) for url in team_urls] 
    return list(zip(team_names, team_urls))
    
def get_league_table():
    
    standing_url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    data = pd.read_html(standing_url, match='Regular season Table')
    
    table = data[0]
    table.set_index('Rk', inplace=True)
    table.drop(['Attendance', 'Top Team Scorer', 'Goalkeeper', 'Notes'], axis=1, inplace=True)
    
    return table

def get_fixture_table():
    
    fixtures = {
        'Gameweek': [gw for gw in range(1,39)]
    }
    
    team_urls = get_team_urls()
    team_urls.sort(key=lambda t: t[0])
    for name, url in team_urls:
        data = pd.read_html(url, match = 'Scores & Fixtures')[0]
        data = data[data.Comp == 'Premier League']
        data['Opponent'] = data['Opponent'].apply(lambda x: fbref_to_fpl(x))
        
        fixtures[fbref_to_fpl(name)]= data[['Opponent', 'Venue']].agg('-'.join, axis=1).tolist()
        # Sleep 8s to keep the request rate below fbref limit
        time.sleep(8)
        
    return pd.DataFrame(fixtures).set_index('Gameweek')

