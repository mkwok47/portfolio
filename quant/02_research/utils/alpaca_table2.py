"""
PURPOSE: create and save stock price datasets locally with SQLITE3
so don't need to keep re-calling data API
(time-consuming for minutely-level data)

Scenarios upon 'obtaining' a table:
    1. table doesn't exist: action=None
    2. table exists and just want the table as-is: action=None
    3. table exists and just want to append -> action='update'
    4. table exists but want to replace entirely -> action='replace'

5 sqlite3 datatypes:
    1. null,
    2. integer,
    3. real (float),
    4. text,
    5. blob (as-is, e.g. image)
    
Delete vs drop:
    - Delete: removes only the rows in tablem preserves table structure
    - Drop: removes all data in the table and table structure
"""

import sqlite3
import pandas as pd
import sys
# sys.path.append(<PATH>)
import alpaca_data


def obtain_table(ticker, timeframe, action=None, start_date='2020-07-01'):
    
    """
    action can be 'update' or 'replace', otherwise None by default
    timeframe = 1Min, 2Min, ..., 59Min
    """
    # db_path = <PATH>.db  
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # FUNCTIONS ===============================================================
    
    def df_to_table(ticker, df, timeframe, drop=False):
        
        if drop:
            c.execute(f"""
                      DROP TABLE IF EXISTS {ticker + timeframe}
                      """)
            
        c.execute(f"""
                  CREATE TABLE IF NOT EXISTS {ticker + timeframe} 
                  (timestamp datetime primary key, 
                   open real(15,5), 
                   high real(15,5), 
                   low real(15,5), 
                   close real(15,5), 
                   volume integer, 
                   trade_count integer, 
                   vwap real(15,5))
                  """)
        conn.commit()
        df.to_sql(ticker + timeframe, conn, if_exists='append', index=False)

    def fetch_data_api():
        api_df = alpaca_data.intra_adj(ticker, timeframe, start_date)
        api_df.reset_index(inplace=True)
        return api_df

    def fetch_table():
        c.execute(f'''SELECT * FROM {ticker + timeframe}''')
        table_df = pd.DataFrame(c.fetchall(), columns=['timestamp','open','high','low','close','volume','trade_count','vwap'])
        table_df['timestamp'] = pd.to_datetime(table_df['timestamp'])
        table_df.set_index('timestamp', drop=True, inplace=True)
        table_df = table_df[table_df.index>=start_date]
        return table_df
    
    # SCRIPT ==================================================================
    
    if action is None:
            
        while True:
            try: # fetch as-is
                table_df = fetch_table()
                print(f'table {ticker + timeframe} successfully obtained')
                return table_df
            except: # table doesn't exist, create
                print(f'table {ticker + timeframe} nonexistent, creating now')
                api_df = fetch_data_api()
                df_to_table(ticker, api_df, timeframe)
                
    elif action == 'update':
        print(f'updating table {ticker + timeframe}')
        
        api_df = fetch_data_api()
        
        try: # find new records to append
            api_df['timestamp_str'] = api_df['timestamp'].astype(str)
            table_df = fetch_table()
            table_df.reset_index(inplace=True)
            table_df['timestamp_str'] = table_df['timestamp'].astype(str)
            new_df = api_df[~api_df['timestamp_str'].isin(table_df['timestamp_str'])]
            new_df.drop(columns='timestamp_str', inplace=True)
            print(f'obtained set of {len(new_df)} records not yet in table')
            df_to_table(ticker, new_df, timeframe)
        except: # table doesn't exist, create
            print(f'table {ticker + timeframe} nonexistent, creating now')
            api_df.drop(columns='timestamp_str', inplace=True)
            df_to_table(ticker, api_df, timeframe)
        
        table_df = fetch_table()
        print(f'table {ticker + timeframe} successfully obtained')
        return table_df
        
    elif action == 'replace':
        print(f'replacing table {ticker + timeframe}')
        
        api_df = fetch_data_api()
        df_to_table(ticker, api_df, timeframe, drop=True)
        
        table_df = fetch_table()
        print(f'table {ticker + timeframe} successfully obtained')
        return table_df
        
    else:
        raise ValueError("action can be 'update' or 'replace', otherwise None by default")
        
if __name__ == '__main__':
    test_df = obtain_table('LABU', '59Min', start_date='2021-03-20')
    display(test_df)
    
    if not test_df.equals(test_df.reset_index().sort_values('timestamp').set_index('timestamp',drop=True)):
        raise ValueError("may need to add df.sort_values('timestamp', inplace=True) logic")
        
