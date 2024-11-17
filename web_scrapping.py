import requests
from bs4 import BeautifulSoup
from io import StringIO

standings_url = "https://www.flashscore.fr/football/maroc/botola-pro/#/rgOPXZ5h/table/overall"
data = requests.get(standings_url)


soup = BeautifulSoup(data.text, features="lxml")
standings_table = soup.select('table.stats_table')[0]
links = standings_table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l]

team_urls = [f"https://fbref.com{l}" for l in links]
data = requests.get(team_urls[0])

import pandas as pd
matches = pd.read_html(StringIO(data.text), match="Scores & Fixtures")[0]

soup = BeautifulSoup(data.text, features="lxml")
links = soup.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if l and 'all_comps/shooting/' in l]

data = requests.get(f"https://fbref.com{links[0]}")


shooting = pd.read_html(StringIO(data.text), match="Shooting")[0]

print(shooting.head())