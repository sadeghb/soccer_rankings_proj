"""
This file includes a function that merges the several hundred tables extracted
from the transfermarkt website into one dataframe and saves it to a CSV file.

Technically, there are two main functions: one that only merges said tables,
and another that contains additional customization for the particular
purpose of this project. Only the customized data frame is saved.

The additional customizations include , but are not limited to,
standardizations of market values, scaling of # of points and other variables
to make them meaningful across different leagues.

"""

import pandas as pd
from sklearn.preprocessing import StandardScaler

league_info = pd.read_csv('league_info.csv', index_col='Country')

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
        f'./Standings/S_{code}{tier}_{str(year)[-2:]}.csv',
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
        f'./Market Values/MV_{code}{tier}_{str(year)[-2:]}.csv',
        index_col='Club'
        )
    df.index = df.index.str.strip()
    return df

def df_organizer(
        countries:list[str],years:list[int],tiers:list[int]
        ) -> pd.DataFrame:
    
    s_cols = ['Rank', 'Pld', 'W', 'D', 'L', 'Goals', '+/-', 'Pts']
    mv_cols = ['Rank', 'Squad', 'Avg Age', 'Foreigners', 'Avg Player Value (m)', 'Value (m)']
    df = pd.DataFrame()
    for country in countries:
        df_country = pd.DataFrame()
        for year in years:
            df_year = pd.DataFrame()
            for tier in tiers:
                s = load_s(country, year, tier)
                s.index = s.index.str.strip()
                s = s[s_cols]    
                mv = load_mv(country, year, tier)
                mv = mv[mv_cols]
                mv.rename(columns={'Rank':'VRank'}, inplace=True)
                df_tier = pd.concat([s,mv], axis=1)
                df_tier.columns = [(year,f'Tier {tier}',col) for col in df_tier.columns]
                df_year = pd.concat([df_year,df_tier],axis=0)
            if df_country.empty:
                df_country = df_year
            else:
                df_country = df_country.merge(df_year,how='outer',on='Club')
        df_country.index = [(country, club) for club in df_country.index]
        df = pd.concat([df, df_country], axis=0)
        
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.index = pd.MultiIndex.from_tuples(df.index)
    return df

def scale(column):
    scaler = StandardScaler()
    return scaler.fit_transform(column)#.to_numpy().reshape(-1,1))

def df_customizer(
        countries:list[str],years:list[int],tiers:list[int]
        ) -> pd.DataFrame:
    
    s_cols = ['League', 'Year', 'Rank', 'W', 'D', 'L', '+/-', 'Pts', 'Goals_For', 'Goals_Against']
    mv_cols = ['Rank', 'Squad', 'Avg Age', 'Foreigners', 'Avg Player Value (m)', 'Value (m)']
    df = pd.DataFrame()
    for country in countries:
        df_country = pd.DataFrame()
        for year in years:
            df_year = pd.DataFrame()
            for tier in tiers:
                s = load_s(country, year, tier)
                s.index = s.index.str.strip()
                pld = s['Pld']
                n_teams = len(s)
                s['Goals_For'] = s['Goals'].str.split(':').apply(lambda s: float(s[0]))
                s['Goals_Against'] = s['Goals'].str.split(':').apply(lambda s: float(s[1]))
                s = s[s_cols]
                s['Rank_SC'] = s['Rank'] / n_teams
                s['W_SC'] = s['W'] / pld
                s['D_SC'] = s['D'] / pld
                s['L_SC'] = s['L'] / pld
                s['+/-_SC'] = s['+/-'] / pld
                s['Pts_SC'] = s['Pts'] / pld
                s['Goals_For_SC'] = s['Goals_For'] / pld
                s['Goals_Against_SC'] = s['Goals_Against'] / pld
                s = s.drop(
                    ['W','D','L','+/-','Pts','Goals_For',
                     'Goals_Against'],axis=1)
                
                mv = load_mv(country, year, tier)
                mv = mv[mv_cols]
                mv.rename(columns={'Rank':'VRank'}, inplace=True)
                mv['VRank_SC'] = mv['VRank'] / n_teams
                mv['Avg_Player_Value_(m)_SC'] = scale(mv['Avg Player Value (m)'].values.reshape(-1, 1))
                mv['Value_(m)_SC'] = scale(mv['Value (m)'].values.reshape(-1, 1))
                mv['Squad_SC'] = scale(mv['Squad'].values.reshape(-1, 1))
                mv['Avg_Age_SC'] = scale(mv['Avg Age'].values.reshape(-1, 1))
                mv['Foreigners_SC'] = scale(mv['Foreigners'].values.reshape(-1, 1))
                mv = mv.drop(
                    ['VRank','Avg Player Value (m)','Value (m)','Squad', 'Avg Age', 'Foreigners'], axis=1)
                
                df_tier = pd.concat([s,mv], axis=1)
                df_tier.columns = [(year,f'Tier {tier}',col) for col in df_tier.columns]
                df_year = pd.concat([df_year,df_tier],axis=0)
            if df_country.empty:
                df_country = df_year
            else:
                df_country = df_country.merge(df_year,how='outer',on='Club')
        df_country.index = [(country, club) for club in df_country.index]
        df = pd.concat([df, df_country], axis=0)
        
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.index = pd.MultiIndex.from_tuples(df.index)
    return df


countries = league_info.index
years = range(2005,2023)
tiers = [1,2]

# df_organized = df_organizer(countries, years, tiers)
df_customized = df_customizer(countries, years, tiers)
df_customized.to_csv('merged_tables.csv')