#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 00:07:25 2022

CRONTAB 6:20am

@author: michaelkwok
"""

script_name = 'SAMPLE'
contact = not production
capital = 5000
account_min = 26000
account_goal = 50000

global_message = ''

def run_script(production):
    
    import smtplib, ssl
    from datetime import datetime, date
    import pytz
    import time
    import traceback
    import json
    
    from tda import auth, client
    from tda.orders.common import EquityInstruction, OrderType, Session, \
        Duration, OrderStrategyType
    from tda.orders.generic import OrderBuilder
    from alpaca_trade_api.rest import REST
   
    from production_functions import send_email, handle_message, sleep_func, auth_tda, check_delist, \
        get_last_price, buy_market, sell_market
    import stock_list
    
    try:
    
        handle_message(f'\nRunning {script_name} with production {production} and capital {capital} \
                       at {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
        account_id = 
        tickers = stock_list.tickers
    
        # daylight savings time
        if datetime.now(pytz.timezone("US/Pacific")).tzinfo._dst != 0:  # is DST
            handle_message('\n\nDST: true, continuing script')
        else:  # is NOT DST
            handle_message('\n\nDST: false, sleeping for 1 hour')
            if production:
                time.sleep(60*60)
                
        # ALPACA API
        headers = json.loads(open("key_real.txt",'r').read())
        trading_url = 'https://api.alpaca.markets'
        trading_api = REST(headers["APCA-API-KEY-ID"], headers["APCA-API-SECRET-KEY"], base_url=trading_url)
        
        # check market open
        if (not trading_api.get_clock().is_open): # note, get_clock is EST
            contact = True
            handle_message('\n\nALERT: Market is currently not open. No trade.', raise_error=production)
            
        # check early close
        if trading_api.get_clock().next_close.time().hour!=16: # note, get_clock is EST
            handle_message(f'\n\nEarly close today: \
                           {trading_api.get_clock().next_close.time().isoformat()} EST. No sleep.')
        else:
            wake_time = '12:38:00'
            sleep_func(wake_time)

    # =============================================================================
    # ENTRY
    # =============================================================================
        
        c = auth_tda()
        notional = round(capital / len(tickers), 2)
        
        for ticker in tickers:
            
            delisted = check_delist(ticker)
            if delisted:
                contact = True
                handle_message(f'\n\nRED ALERT: delisted stock found: {ticker}')
                script_name += ' (RED ALERT DELIST) '
                continue
            
            last_price = get_last_price(ticker)
            qty = notional // last_price
            if qty > 0:
                handle_message(f'\n\nBuying market ${notional} ({qty} shares at last_price {last_price}) \
                               of {ticker} at {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
                if production:
                    buy_market(ticker, qty)
            else:
                handle_message(f'\n\n{ticker} qty is 0, no buy at \
                               {datetime.now(pytz.timezone("US/Pacific")).time()} PST')

    # =============================================================================
    # EXIT
    # =============================================================================
                    
    # (REMOVED)

    # =============================================================================
    # DELIST
    # =============================================================================
        
        c = auth_tda()
        
        for ticker in tickers:
            
            delisted = check_delist(ticker)
            if delisted:
                contact = True
                handle_message(f'\n\nRED ALERT: delisted stock found: {ticker}')
                script_name += f' (RED ALERT DELIST: {ticker}) '
                continue
            
    # =============================================================================
    # ACC BAL
    # =============================================================================
            
        c = auth_tda()
        account = c.get_account(account_id)
        account_bal = account.json()['securitiesAccount']['currentBalances']['liquidationValue']
        # cashBalance is actual cash, liquidationValue is total account
        handle_message(f'\n\nAccount balance: {account_bal}')
        if account_bal < account_min:
            contact = True
            handle_message(f'\n\nRED ALERT: account balance is below {account_min}: {account_bal}')
            script_name += f' (RED ALERT ACC_BAL: {account_bal}) '
        if account_bal > account_goal:
            contact = True
            handle_message(f'\n\nGREEN ALERT: account balance is above {account_goal}: {account_bal}')
            script_name += ' (GREEN ALERT ACC_BAL) '
        
        handle_message('\n\nScript completed, sending email')
        send_email()
        
    except:
        contact = True
        handle_message(f'\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nCode failed and \
                       halted at {datetime.now(pytz.timezone("US/Pacific"))} PST')
        handle_message(f'\nException traceback: \n\n{traceback.format_exc()}')
        script_name += ' (FAILED) '
        send_email()
        
