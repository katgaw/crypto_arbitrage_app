import pandas as pd
import numpy as np

def manipulate_kraken_kucoin(df_kraken_kucoin):
    ''' Merge the Kraken DataFrame with the Kucoin DataFrame and turn the new DataFrame into desirable format.

    Args:
        df_kraken_kucoin (list): List of consisting of the Kraken and Kucoin DataFrames.

    Returns:
        One DataFrame consisting of Kraken and Kucoin 
    '''

    kraken_pd=df_kraken_kucoin[0] #obtain the Kraken dataframe
    kucoin_pd=df_kraken_kucoin[1] #obtain the Kucoin dataframe

    # Merge the two dataframes
    df_kraken_kucoin_all=kraken_pd.merge(kucoin_pd,left_on=['date','coin'],right_on=['date1','coin'],how='outer').drop(columns=['date'])

    # Manipulate Kucoin_Kraken DataFrame into desirable format
    df_kraken_kucoin_all.columns=['coin','kraken_price','date1','kucoin_price'] #rename columns
    df_kraken_kucoin_all['date1']=pd.to_datetime(df_kraken_kucoin_all['date1']) #turn the date1 column into datetime format
    df_kraken_kucoin_all['coin']=df_kraken_kucoin_all['coin'].astype(object) #make sure the coin column is in object format
    return(df_kraken_kucoin_all)

def biggest_arbitrage_opportunity(symbols_all,grouped,exchanges,daily_returns):
    ''' Search through the arbitrage options for the most profitable ones on average.
        This function helps to select the most profitable arbitrage opportunities.

    Args:
        symbols_all (list): List of currency symbols.
        grouped: grouped dataframe by coin.
        exchanges (list): List of exchanges we look through.
        daily_returns (DataFrame): DataFrame in absolute values or as daily returns.

    Returns:
        One DataFrame with values for the average profit from arbitrage for every currency and for every pair of exchanges.
    '''

    coin_name=[] #declare empty list, it will consists of all the coin names.
    exchange_coin=pd.DataFrame() #declare empty dataframe, it will be the final dataframe.

    for symbol in symbols_all:  
        ''' Loop through the symbols to obtain the average profit for every currency. '''
        group_coin=grouped.get_group(symbol) #from the grouped dataframe get group for the symbol.
        differences=[] #declare empty list, it will consists of the values for the average profit
        exchange_diff_all=pd.DataFrame({'exchanges':exchanges})
        exchange_diff_all.set_index('exchanges',inplace=True)

        for exchange in ['kraken','kucoin','bitmex','bittrex','gemini']:
            ''' Loop through the exchanges to obtain the average profit for every pair of exchanges.'''
            exchange_index=list(exchanges).index(exchange)
            exchange_coin1=group_coin[daily_returns.columns[exchange_index+1]]
            num_of_coins=10000/exchange_coin1
            differences=[] #declare empty list, it will consists of the values for the average profit
            
            for each_exchange in ['kraken','kucoin','bitmex','bittrex','gemini']:
                ''' Get the average profit for the exchange in the loop with respect to every other exchange.'''
                exchange_index1=list(exchanges).index(each_exchange)
                exchange_coin2=group_coin[daily_returns.columns[exchange_index1+1]]
                # the main equation calculating the average profit
                difference=((abs(exchange_coin2-exchange_coin1)*num_of_coins)/abs(exchange_coin1)*num_of_coins).mean()
                differences=np.append(differences,difference)
            exchange_diff=pd.DataFrame({'exchanges':exchanges,exchange:differences})
            exchange_diff.set_index('exchanges',inplace=True)
            exchange_diff_all=pd.concat([exchange_diff_all,exchange_diff],axis=1)
        exchange_coin=pd.concat([exchange_coin,exchange_diff_all],axis=0) #create the final dataframe which in every loop adds dataframe for new currency.
        coin_name=np.append(coin_name,np.repeat(symbol,len(exchange_diff_all))) #get column of coin names in the size fitting the final DataFrame.

    exchange_coin.insert(0,'coin',coin_name) #Populate the DataFrame with coin names.
    return exchange_coin