"""
This file includes two functions to scrape league/club data from the
transfermarkt website.

"""

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

league_info = pd.read_csv('league_info.csv', index_col='Country')

def get_standings(country:str, year:int, tier:int=1) -> pd.DataFrame:
    """
    This function extracts from the transfermarkt website the final standings
    of the league season corresponding to the parameters entered.
    
    Parameters
    ----------
    country : str
        Full name of the country according to the transfermarkt database.
        See README for available countries.
    year : int
        The year in which the season ends.
        See README for available years.
    tier : int
        Tiers 1 and 2 are supported.

    Returns
    -------
    standings : pd.DataFrame
        The league standings corresponding to the country, year and tier
        entered. Descriptions of columns are as follows:
            Rank: final ranking
            Club: full name of the club
            Pld: # of games played
            W: # of wins
            D: # of draws
            L: # of losses
            Goals: # of goals scored, # of goals conceded
            +/-: # of goals scored minus # of goals conceded
            Pts: # of points
            League: summarizing country + tier
            year: year in which the season ends

    """
    
    # Generating the URL containing the standings
    code = 'Code'
    division = f'Tier {tier}'
    url = f'https://www.transfermarkt.us/{league_info.loc[country,division]}/tabelle/wettbewerb/{league_info.loc[country,code]}{tier}?saison_id={year-1}'
        
    # Mimicking the Google Chrome browser
    headers = ({'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'})    
    r = requests.get(url,headers=headers)
    page = r.content
    
    success = (200 <= r.status_code < 300)
    if not success:
        print(f'Error: {country}, {year}, {tier}')
        return
    
    soup = bs(page, 'lxml')
    table = soup.find('table',{'class':'items'})
    if not table:
        print(f'Error: {country}, {year}, {tier}')
        return
    
    # Extracting the list of the clubs from the response content; otherwise
    # the clubs would appear abbreviated, which would be inconsistent with
    # other tables

    clubs_list = []
    for item in table.find_all('tr')[1:]:
        clubs_list.append(item.find('a')['title'])        
    
    # Extracting, fixing and prettifying the table
    standings = pd.read_html(page)[1]
    standings = standings.drop(['Club'],axis=1)
    standings = standings.rename(columns={'#':'Rank','Club.1':'Club','Unnamed: 3':'Pld'})
    standings['Club'] = clubs_list
    standings['League'] = league_info.loc[country,'Code']+str(tier)
    standings['Year'] = year

    return standings




def get_market_values(country:str, year:int, tier:int=1) -> pd.DataFrame:
    """
    This function extracts from the transfermarkt website some information,
    most importantly the market values of the clubs in the league season
    corresponding to the parameters entered.
    
    Parameters
    ----------
    country : str
        Full name of the country according to the transfermarkt database.
        See README for available countries.
    year : int
        The year in which the season ends.
        See README for available years.
    tier : int
        Tiers 1 and 2 are supported.

    Returns
    -------
    market_values : pd.DataFrame
        Some club information for the league season corresponding to
        the parameters entered.
        The list and descriptions of columns are as follows:
            VRank: market value ranking
            Club: full name of the club
            Squad: size of the squad
            Avg Age
            Foreiners: # of foreign players
            Avg Player Value: average of the players' market values
            Value: market value
            League: summarizing country + tier
            year: year in which the season ends           
            
    """
    
    # Generating the URL containing the market values
    code = 'Code'
    division = f'Tier {tier}'
    url = f'https://www.transfermarkt.us/{league_info.loc[country,division]}/startseite/wettbewerb/{league_info.loc[country,code]}{tier}/plus/?saison_id={year-1}'
    
    # Value fix to make all values float, and in million euros
    def value_fix(value):
        if value and value != '-':
            if value[-1] == 'm':
                return float(value[1:-1])
            elif value[-1] == 'k':
                return float(value[1:-1])/1000
            elif value[-2:] == 'bn':
                return float(value[1:-2])*1000

    headers = ({'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'})
    
    r = requests.get(url,headers=headers)

    success = 200 <= r.status_code < 300
    if not success:
        print(f'Error: {country}, {year}, {tier}')
        return

    page = r.content
    
    # Extracting, fixing and prettifying the table
    market_values = pd.read_html(page)[1]
    market_values = market_values.iloc[:-1,1:7]
    columns = ['Club','Squad','Avg Age', 'Foreigners', 'Avg Player Value (m)', 'Value (m)']
    market_values.columns = columns
    market_values['Squad'] = market_values['Squad'].apply(int)
    market_values['Foreigners'] = market_values['Foreigners'].apply(int)
    market_values['Avg Player Value (m)'] = market_values['Avg Player Value (m)'].apply(value_fix)
    market_values['Value (m)'] = market_values['Value (m)'].apply(value_fix)
    market_values['League'] = league_info.loc[country,'Code']+str(tier)
    market_values['Year'] = year
    market_values.insert(loc=0, column='VRank', value=range(1,len(market_values)+1))
    
    return market_values