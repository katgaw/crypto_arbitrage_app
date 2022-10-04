''' This Script contains functions for scraping selected cryptocurrency exchanges. '''

# Import Libraries
import pandas as pd
import numpy as np
import os
import krakenex
from pykrakenapi import KrakenAPI
from kucoin.client import Client
import requests

def scrape_kraken_kucoin(symbols_all,start_day,end_day):
    '''Scrape Kraken and Kucoin crypto exchanges and return two dataframes, one for Kraken and one for Kucoin exchanges.
    
    Args:
        symbols_all (list): List of currency symbols.
        start_day (str): Day when you want to start scraping.
        end_day (str): Day when you want to stop scraping.

    Returns:
        Two dataframes, one for Kucoin and one for Kraken, with columns for date, coin name and closing price. 
    '''

    #import extra libraries for this function
    import time
    import datetime

    kraken_pd_all=pd.DataFrame()
    kucoin_pd_all=pd.DataFrame()

    # SET API KEYS
    #   - for Kraken
    k = krakenex.API()
    api_key_kraken = os.getenv('Kraken_API_Key')
    api_secret_kraken = os.getenv('Kraken_Private_Key')

    #   - for Kucoin
    api_key_kucoin = os.getenv('KC_Key')
    api_secret_kucoin = os.getenv('KC_Secret')
    api_passphrase_kucoin = os.getenv('KC_Passphrase')
    client = Client(api_key_kucoin, api_secret_kucoin, api_passphrase_kucoin)

    for symbol in symbols_all:
        ''' Iterate over the list with the selected symbols of currencies and in every loop scrape an exchange 
        for one currency, create dataframe with date, coin name and closing price. Concat these dataframes across 
        all the selected currencies and create final dataframe for each exchange.
        '''
        #------------- Scrape Kraken
        # Inspired by: https://docs.kraken.com/rest/#tag/Market-Data/operation/getOHLCData
        ticker_name=[]
        api = krakenex.API()
        k = KrakenAPI(api)
        # Scrape the exchange
        ohlc = k.get_ohlc_data(symbol+'USD', since=start_day,interval=60, ascending = True)
        # Create dataframe from the result
        kraken_pd=pd.DataFrame({'close':ohlc[0]['close']}).reset_index()
        # Create list with the currency symbol in the length of the scraped dataset
        ticker_name=np.append(ticker_name,np.repeat(symbol,len(kraken_pd)))
        # Insert the currency list to the scraped dataset
        kraken_pd.insert(1,'coin',ticker_name)
        # Rename the columns
        kraken_pd.columns=['date','coin','close']
        # Concat the DataFramen in the loop with the previous ones, to obtain the DataFrame consisting of all the currencies.
        kraken_pd_all=pd.concat([kraken_pd_all,kraken_pd],axis=0)

        #------------ Scrape Kucoin
        # Inspired by: https://python-kucoin.readthedocs.io/en/stable/market.html
        ticker_name=[]
        kucoin=[]
        # Scrape the exchange
        klines = client.get_kline_data(symbol+'-USDT', '1hour', int(start_day), int(end_day)) #1hour
        for value in klines:
            kucoin=np.append(kucoin,value[1])
        #Define date column
        start_date = datetime.datetime.fromtimestamp(int(start_day))
        end_date = datetime.datetime.fromtimestamp(int(end_day))
        all_dates=pd.date_range(start_date,end_date,freq='H').sort_values(ascending=False) #1min
        #Define Ticker column
        ticker_name=np.append(ticker_name,np.repeat(symbol,len(kucoin)))
        # Create dataframe from the result with three columns
        kucoin_pd=pd.DataFrame({'date1':all_dates[:-1],'coin':ticker_name,'close':kucoin})
        # Sort the datefame by the date to get ascending values as we got for the Kraken exchange.
        kucoin_pd=kucoin_pd.sort_values(by=['date1'], ascending=True)
        # Concat the DataFrame in the loop with the previous ones, to obtain the DataFrame consisting of all the currencies.
        kucoin_pd_all=pd.concat([kucoin_pd_all,kucoin_pd],axis=0)
        time.sleep(5) #sleep the scraping for 5 seconds to avoid an excessive scraping error.
    return [kraken_pd_all,kucoin_pd_all]

def scrape_exchanges(symbols_all,symbols_bitmex,urls):
    '''Scrape Bittmex, Bittrex and Gemini crypto exchanges and return a dataframe with scraped data for these exchanges.
    
    Args:
        symbols_all (list): List of currency symbols, applicable for scraping Bittrex and Gemini.
        symbols_bitmex (list): List of currency symbols, applicable for scraping Bittmex.
        urls (list): List of base urls (url string before a symbol for a currency is required) used for scraping. The URLs follow the order: Bitmex, Bittrex and Gemini.

    Returns:
        One dataframe for Bittmex, Bittrex and Gemini crypto exchanges, with columns for date, coin name and closing price. 
    '''
    
    #import extra libraries for this function
    from datetime import datetime
    from datetime import timezone

    df_all=pd.DataFrame() # Create empty DataFrame
    loop=0 # Determine variable which will count how many loops we had done

    for url_base in urls:
        ''' Iterate over the list of urls for different exchanges and create the final DataFrame.
        '''
        if loop==0:
            symbols=symbols_bitmex # when scraping Bitmex use the coin symbols in the form it requires,
        else:
            symbols=symbols_all # for scraping Bittrex and Gemini use these coin symbols.
        df_together=pd.DataFrame()
        for symbol in symbols:
            ''' Iterate over the list of coin symbols'''
            # Declare empty lists for future columns (date, closing price and currency name) in a DataFrame.
            date_column=[]
            close_column=[]
            ticker_name=[]

            # Create url link with the selected currency symbol.
            if loop==0:
                url=url_base+f'{symbol}&count=1000&reverse=false&startTime=2022-08-14'
            if loop==1:
                url=url_base+f'{symbol}-USD/candles/HOUR_1/recent'
            if loop==2:
                url=url_base+f'{symbol.lower()}usd/1hr'
            
            # Scrape the exchange
            df=requests.get(url).json()

            # Feed the scraped data into the date and closing price columns
            for time in df:
                if loop==0:
                    date_column=np.append(date_column,time['timestamp'])
                if loop==1:
                    date_column=np.append(date_column,time['startsAt'])
                if loop==2:
                    date_column=np.append(date_column,time[0])
                    
            for close in df:
                if loop==2:
                    close_column=np.append(close_column,close[4])
                else:
                    close_column=np.append(close_column,close['close'])

            #Create dataframe with the date and closing price columns
            coin_pd=pd.DataFrame({'date':date_column,'close':close_column})
            #Transform the date into a nice format
            date_column_nice=[]
            for date in coin_pd['date']:
                if loop==1:
                    date=str(date.replace(':00:',':00:00.0')) #For Bittrex the characters in the date format need to be changed.
                if loop==2:
                    import datetime
                    date_nice=datetime.datetime.fromtimestamp(int(date/1000)) # Transform from timestamp into a date.
                else:
                    date_nice=datetime.fromisoformat(date[:-1]).astimezone(timezone.utc)
                # Finally, append nice date format to the date column.
                date_column_nice=np.append(date_column_nice,date_nice.strftime('%Y-%m-%d %H:%M:%S'))
            # Create currency name column in the length of the date column.
            ticker_name=np.append(ticker_name,np.repeat(symbols_all[list(symbols).index(symbol)],len(date_column)))
            # Feed the date column in a date format to the DataFrame.
            coin_pd['date']=pd.to_datetime(date_column_nice)
            # Feed the column with currency names to the DataFrame.
            coin_pd['coin']=ticker_name
            # Rename the DataFrame
            df_together=pd.concat([df_together,coin_pd],axis=0).reset_index().iloc[:,1:] #Reset the index for the DataFrame.

        # Rename the DataFrame and its columns for every exchange
        if loop==0:
            df0=df_together
            df0.columns=['date0','close','coin']
        if loop==1:
            df1=df_together
            df1.columns=['date1','close','coin']
        if loop==2:
            df2=df_together
            df2.columns=['date2','close','coin']
        loop+=1

    # Merge the DataFrames with respect to dates and coin names together.
    df_all=df1.merge(df0,left_on=['date1','coin'],right_on=['date0','coin'],how='outer')
    df_all=df2.merge(df_all,left_on=['date2','coin'],right_on=['date1','coin'],how='outer')

    # Drop excessive date columns.
    df_all=df_all.drop(columns=['date1','date2'])
    # Pop the coin name column and insert it as the first column in the DataFrame.
    coin=df_all.pop('coin')
    df_all.insert(0,'coin',coin)
    # Rename the columns in the DataFrame.
    df_all.columns=['coin','price_bitmex','price_bitrex','date','price_gemini']
    # Set date as an index in the final DataFrame.
    df_all.set_index('date',inplace=True)
    return df_all