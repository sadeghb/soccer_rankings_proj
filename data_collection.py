"""
Created on Wed May  3 10:35:47 2023

@author: bolouki

This file collects the data we need from the transfermarkt website.

See README for the leagues and years of interest.

"""

import pandas as pd
import transfermarkt_scraper
from transfermarkt_scraper import get_standings, get_market_values

league_info = pd.read_csv('league_info.csv', index_col='Country')

max_attempts = 20
countries = league_info.index
years = range(2005,2024)
tiers = [1,2]

# Collecting the standings

res_s = []

for country in countries:
    for year in years:
        for tier in tiers:
            res_s.append((country,year,tier))
            
attempt = 0
while attempt < max_attempts and len(res_s) > 0:
    attempt += 1
    failed = []
    for country, year, tier in res_s:
        code = league_info.loc[country,'Code']
        standings = get_standings(country, year, tier)
        if not isinstance(standings, pd.DataFrame):
            failed.append((country,year,tier))
        else:
            standings.to_csv(f'./standings/S_{code}{tier}_{str(year)[-2:]}.csv',index=False)
    res_s = failed.copy()

if res_s:
    print('Failed to download all. Check out <res_s> for what remains.')
else:
    print('Success -- Downloaded all!')

# Collecting the market values and club info

res_mv = []

max_attempts = 20
countries = league_info.index
years = range(2005,2025)
tiers = [1,2]

for country in countries:
    for year in years:
        for tier in tiers:
            res_mv.append((country,year,tier))
            
attempt = 0
while attempt < max_attempts and len(res_mv) > 0:
    attempt += 1
    failed = []
    for country, year, tier in res_mv:
        code = league_info.loc[country,'Code']
        market_values = get_market_values(country, year, tier)
        if not isinstance(market_values, pd.DataFrame):
            failed.append((country,year,tier))
        else:
            market_values.to_csv(f'./market_values/MV_{code}{tier}_{str(year)[-2:]}.csv',index=False)
    res_mv = failed.copy()

if res_mv:
    print('Failed to download all. Check out <res_mv> for what remains.')
else:
    print('Success -- Downloaded all!')
