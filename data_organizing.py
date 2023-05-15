"""
This file includes a function that merges the several hundred tables extracted
from the transfermarkt website into one dataframe and saves it to a CSV file.

It also includes two helper functions for loading standings and market values
tables given a country, year and tier of interest.

"""

import pandas as pd

# Loading the metadata of the leagues

league_info = pd.read_csv('league_info.csv', index_col='Country')

# Two helper functions for loading standings and market values tables

def load_s(country:str, year:int, tier:int) -> pd.DataFrame:
    """
    Parameters
    ----------
    country : str
        See README for available countries.
    year : int
        See README for available countries.
    tier : int
        See README for available countries.

    Returns
    -------
    df : Pandas DataFRame
        The standings table corresponding to the country, year, tier entered.

    """
    code = league_info.loc[country,'Code']
    df = pd.read_csv(
        f'./standings/S_{code}{tier}_{str(year)[-2:]}.csv',
        index_col='Club'
        )
    df.index = df.index.str.strip()
    return df

def load_mv(country:str, year:int, tier:int) -> pd.DataFrame:
    """
    Parameters
    ----------
    country : str
        See README for available countries.
    year : int
        See README for available countries.
    tier : int
        See README for available countries.

    Returns
    -------
    df : Pandas DataFRame
        The market values table corresponding to the country, year, tier
        entered.

    """
    code = league_info.loc[country,'Code']
    df = pd.read_csv(
        f'./market_values/MV_{code}{tier}_{str(year)[-2:]}.csv',
        index_col='Club'
        )
    df.index = df.index.str.strip()
    return df

# A function to load and merge all tables given countries, years
# and tiers of interest;
# Shall be used mainly for viewing purposes.

def all_tables(countries, years, tiers):
    s_cols = ['Rank', 'Pld', 'W', 'D', 'L', 'Goals_For', 'Goals_Against', '+/-', 'Pts', 'League']
    mv_cols = ['Rank', 'Squad', 'Avg Age', 'Foreigners', 'Avg Player Value (m)', 'Value (m)']
    df = pd.DataFrame()

    for country in countries:
        for year in years:
            for tier in tiers:
                s = load_s(country, year, tier)
                s.index = s.index.str.strip()
                s['Goals_For'] = s['Goals'].str.split(':').apply(lambda s: float(s[0]))
                s['Goals_Against'] = s['Goals'].str.split(':').apply(lambda s: float(s[1]))
                s = s[s_cols]
                
                mv = load_mv(country, year, tier)
                mv = mv[mv_cols]
                mv.rename(columns={'Rank':'VRank'}, inplace=True)
                
                smv = pd.concat([s,mv], axis=1)
                smv = smv.reset_index()
                idx_cols = ['Country', 'Year', 'Tier']
                smv[idx_cols] = [country, year, tier]
                idx_cols.append('Club')
                smv = smv.set_index(idx_cols)
                
                df = pd.concat([df, smv], axis=0)

    return df


countries = league_info.index
years = range(2005,2023)
tiers = [1,2]

merged_tables = all_tables(countries, years, tiers)
merged_tables.to_csv('merged_tables.csv')