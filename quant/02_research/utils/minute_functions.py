#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 02:47:27 2022

NOTES
- premarket < 6:30
- 6:30 <= regular < 13
- 13 <= aftermarket

@author: michaelkwok
"""

import datetime
import pandas as pd
import alpaca_table2

market_open_time = datetime.time(6,30)
market_close_time = datetime.time(13)

# =============================================================================
# Functions
# =============================================================================

def view_utc_offsets(df_input):
    
    df = df_input.copy(deep=True)
    unique_time_diffs = df['timestamp_pacific_str'].str[-5:].unique()
    print(unique_time_diffs)
    for unique_time_diff in unique_time_diffs:
        print(unique_time_diff, len(df[df['timestamp_pacific_str'].str[-5:] == unique_time_diff]))
    if len(unique_time_diffs) != 2:
        raise ValueError('check utc offset')
    
def obtain_data(tickers, timeframes, action=None, start_date='2000-01-01', end_date=str(datetime.datetime.today().date() - datetime.timedelta(days=1)), min_length=100):
    
    '''
    note: unique_dates will be in pacific time
    '''
    
    dicts = {ticker:{timeframe:{} for timeframe in timeframes} for ticker in tickers}
    
    for timeframe in timeframes:
        
        for ticker in tickers:
            
            df = alpaca_table2.obtain_table(ticker, timeframe, action=action, start_date=start_date)
            dicts[ticker][timeframe]['df'] = df.copy(deep=True)
            
            dicts[ticker][timeframe]['df']['timestamp_pacific'] = dicts[ticker][timeframe]['df'].index.tz_convert('US/Pacific')
            dicts[ticker][timeframe]['df']['timestamp_pacific_str'] = dicts[ticker][timeframe]['df']['timestamp_pacific'].astype(str)
            
            dicts[ticker][timeframe]['df'] = dicts[ticker][timeframe]['df'][dicts[ticker][timeframe]['df']['timestamp_pacific'] < end_date]
            
            dicts[ticker][timeframe]['df'].loc[(dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.time >= market_open_time) & (dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.time < market_close_time), 'market_hours'] = 'regular'
            dicts[ticker][timeframe]['df'].loc[(dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.time < market_open_time), 'market_hours'] = 'premarket'
            dicts[ticker][timeframe]['df'].loc[(dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.time >= market_close_time), 'market_hours'] = 'aftermarket'
            print(len(dicts[ticker][timeframe]['df']), timeframe)
            view_utc_offsets(dicts[ticker][timeframe]['df'])
            
            # drop sparse data days e.g. holidays and unwanted weekend data + incomplete AM day-of data
            temp_df = dicts[ticker][timeframe]['df'].groupby(dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.date)[['open']].agg(len)
            temp_df.rename(columns={'open': 'num_rows_per_day'}, inplace=True)
            dicts[ticker][timeframe]['df'].reset_index(inplace=True) # preserve timestamp index
            dicts[ticker][timeframe]['df'] = dicts[ticker][timeframe]['df'].merge(temp_df, how='left', left_on=dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.date, right_on=temp_df.index)
            dicts[ticker][timeframe]['df'].drop(columns=['key_0'], inplace=True)
            dicts[ticker][timeframe]['df'].set_index('timestamp', inplace=True)
            
            print('Dropping', len(dicts[ticker][timeframe]['df'][dicts[ticker][timeframe]['df']['num_rows_per_day'] < min_length]), 'rows where num_rows_per_day <', min_length)
            dicts[ticker][timeframe]['df'] = dicts[ticker][timeframe]['df'][dicts[ticker][timeframe]['df']['num_rows_per_day'] >= min_length]
            print('Dropping', len(dicts[ticker][timeframe]['df'][dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.weekday > 4]), 'rows of weekend data')
            dicts[ticker][timeframe]['df'] = dicts[ticker][timeframe]['df'][dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.weekday <= 4]
                        
            dicts[ticker]['unique_dates'] = dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.date.unique()
            print(ticker, len(dicts[ticker]['unique_dates']), 'days')
            print(dicts[ticker][timeframe]['df'].shape)
            display(dicts[ticker][timeframe]['df'].head())
            display(dicts[ticker][timeframe]['df'].tail())
            
    return dicts

def obtain_conjunction(ticker_descript_dict, dicts, timeframe, tail_n=1000000):
    
    '''
    ticker_descript_dict = {'LABU':'bull', 'LABD':'bear'}
    '''
        
    df = dicts[list(ticker_descript_dict.keys())[0]][timeframe]['df'].tail(tail_n).copy(deep=True)
    df = df[(df['timestamp_pacific'].dt.time >= market_open_time) & (df['timestamp_pacific'].dt.time < market_close_time)]
    conjunction_df = pd.DataFrame(index=df.index)

    for ticker in ticker_descript_dict.keys():
        df = dicts[ticker][timeframe]['df'].tail(tail_n).copy(deep=True)
        df = df[(df['timestamp_pacific'].dt.time >= market_open_time) & (df['timestamp_pacific'].dt.time < market_close_time)]
        df['green'] = df['open'] < df['close']
        descript = ticker_descript_dict[ticker]
        df.rename(columns={col:f'{descript}_{col}' for col in df}, inplace=True)
        conjunction_df = conjunction_df.merge(df, left_index=True, right_index=True, how='outer')
        
    dicts[ticker][timeframe]['df']['timestamp_pacific'] = dicts[ticker][timeframe]['df'].index.tz_convert('US/Pacific')
    dicts[ticker][timeframe]['df']['timestamp_pacific_str'] = dicts[ticker][timeframe]['df']['timestamp_pacific'].astype(str)

    descripts = list(ticker_descript_dict.values())    
    for descript in descripts:
        conjunction_df.drop(columns=[f'{descript}_timestamp_pacific', f'{descript}_timestamp_pacific_str'], inplace=True)

    conjunction_df['timestamp_pacific'] = conjunction_df.index.tz_convert('US/Pacific')
    conjunction_df['timestamp_pacific_str'] = conjunction_df['timestamp_pacific'].astype(str)
    view_utc_offsets(conjunction_df)
    
    return conjunction_df

def obtain_daily_attributes(dicts, timeframe, min_length=100):
    
    '''
    uses minutely data to infer daily data (to maintain consistency of data source)
    uses min_length to get rid of unwanted data
    '''
    
    for ticker in dicts.keys():
        
        df = dicts[ticker][timeframe]['df'].copy()
        unique_dates = dicts[ticker]['unique_dates'].copy()
        daily_df = pd.DataFrame(unique_dates, columns=['timestamp']) # timestamp is already pacific
        
        # preferred open (6:30 open)
        temp_df = df[(df['timestamp_pacific'].dt.time==market_open_time)][['timestamp_pacific', 'open']].copy()
        temp_df.rename(columns={'timestamp_pacific':'timestamp_pacific_DROP', 'open':'day_open'}, inplace=True)
        daily_df = daily_df.merge(temp_df, how='left', left_on=daily_df['timestamp'], right_on=temp_df['timestamp_pacific_DROP'].dt.date)
        daily_df.drop(columns=['timestamp_pacific_DROP', 'key_0'], inplace=True)
        
        # backup open (first regular hours min open)
        temp_df = df[df['market_hours']=='regular'].groupby(df['timestamp_pacific'].dt.date)['open'].agg(lambda x: x.iloc[0] if len(x) >= min_length else pd.NA).reset_index().copy()
        temp_df.rename(columns={'timestamp_pacific':'timestamp_pacific_DROP', 'open':'day_open_BACKUP'}, inplace=True)
        daily_df = daily_df.merge(temp_df, how='left', left_on=daily_df['timestamp'], right_on=temp_df['timestamp_pacific_DROP'])
        daily_df.drop(columns=['timestamp_pacific_DROP', 'key_0'], inplace=True)
        
        # high
        temp_df = df[df['market_hours']=='regular'].groupby(df['timestamp_pacific'].dt.date)['high'].agg(lambda x: max(x) if len(x) >= min_length else pd.NA).reset_index().copy()
        temp_df.rename(columns={'timestamp_pacific':'timestamp_pacific_DROP', 'high':'day_high'}, inplace=True)
        daily_df = daily_df.merge(temp_df, how='left', left_on=daily_df['timestamp'], right_on=temp_df['timestamp_pacific_DROP'])
        daily_df.drop(columns=['timestamp_pacific_DROP', 'key_0'], inplace=True) 
        
        # low
        temp_df = df[df['market_hours']=='regular'].groupby(df['timestamp_pacific'].dt.date)['low'].agg(lambda x: min(x) if len(x) >= min_length else pd.NA).reset_index().copy()
        temp_df.rename(columns={'timestamp_pacific':'timestamp_pacific_DROP', 'low':'day_low'}, inplace=True)
        daily_df = daily_df.merge(temp_df, how='left', left_on=daily_df['timestamp'], right_on=temp_df['timestamp_pacific_DROP'])
        daily_df.drop(columns=['timestamp_pacific_DROP', 'key_0'], inplace=True)
        
        # preferred close (13:00 open)
        temp_df = df[(df['timestamp_pacific'].dt.time==market_close_time)][['timestamp_pacific', 'open']].copy()
        temp_df.rename(columns={'timestamp_pacific':'timestamp_pacific_DROP', 'open':'day_close'}, inplace=True)
        daily_df = daily_df.merge(temp_df, how='left', left_on=daily_df['timestamp'], right_on=temp_df['timestamp_pacific_DROP'].dt.date)
        daily_df.drop(columns=['timestamp_pacific_DROP', 'key_0'], inplace=True)
        
        # backup close (last regular hours min close)
        temp_df = df[df['market_hours']=='regular'].groupby(df['timestamp_pacific'].dt.date)['close'].agg(lambda x: x.iloc[-1] if len(x) >= min_length else pd.NA).reset_index().copy()
        temp_df.rename(columns={'timestamp_pacific':'timestamp_pacific_DROP', 'close':'day_close_BACKUP'}, inplace=True)
        daily_df = daily_df.merge(temp_df, how='left', left_on=daily_df['timestamp'], right_on=temp_df['timestamp_pacific_DROP'])
        daily_df.drop(columns=['timestamp_pacific_DROP', 'key_0'], inplace=True)
        
        daily_df.set_index('timestamp', inplace=True)
        print('daily_df created')
        display(daily_df.isna().sum())
        
        # fill missing preferred close with backup close
        if daily_df.isna().sum()['day_close'] > 0:
            print('Filling in', daily_df.isna().sum()['day_close'], 'days of missing preferred close (13:00 open) with backup close (last regular hours min close)')
            daily_df.loc[pd.isna(daily_df['day_close']), 'day_close'] = daily_df['day_close_BACKUP']
        daily_df.drop(columns=['day_close_BACKUP'], inplace=True)
            
        # fill missing preferred open with backup open
        if daily_df.isna().sum()['day_open'] > 0:
            print('Filling in', daily_df.isna().sum()['day_open'], 'days of missing preferred open (6:30 open) with backup open (first regular hours min open)')
            daily_df.loc[pd.isna(daily_df['day_open']), 'day_open'] = daily_df['day_open_BACKUP']
        daily_df.drop(columns=['day_open_BACKUP'], inplace=True)
        
        # return
        dicts[ticker]['day'] = {}
        dicts[ticker]['day']['df'] = daily_df
        dicts[ticker][timeframe]['df'] = dicts[ticker][timeframe]['df'].merge(daily_df, how='left', left_on=dicts[ticker][timeframe]['df']['timestamp_pacific'].dt.date, right_index=True)

    return dicts
