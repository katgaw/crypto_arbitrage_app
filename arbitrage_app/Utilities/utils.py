import pandas as pd
import numpy as np

def manipulate_kraken_kucoin(df_kraken_kucoin):
      kraken_pd=df_kraken_kucoin[0]
      kucoin_pd=df_kraken_kucoin[1]
      df_kraken_kucoin_all=kraken_pd.merge(kucoin_pd,left_on=['date','coin'],right_on=['date1','coin'],how='outer').drop(columns=['date'])

      # Manipulate Kucoin_Kraken DataFrame into desirable format
      df_kraken_kucoin_all.columns=['coin','kraken_price','date1','kucoin_price']
      df_kraken_kucoin_all['date1']=pd.to_datetime(df_kraken_kucoin_all['date1'])
      df_kraken_kucoin_all['coin']=df_kraken_kucoin_all['coin'].astype(object)
      return(df_kraken_kucoin_all)

def biggest_arbitrage_opportunity(symbols_all,grouped,exchanges,daily_returns):
    coin_name=[]
    exchange_coin=pd.DataFrame()

    for symbol in symbols_all:  
        group_coin=grouped.get_group(symbol)
        differences=[]
        exchange_diff_all=pd.DataFrame({'exchanges':exchanges})
        exchange_diff_all.set_index('exchanges',inplace=True)
        for exchange in ['kraken','kucoin','bitmex','bittrex','gemini']:
            exchange_index=list(exchanges).index(exchange)
            exchange_coin1=group_coin[daily_returns.columns[exchange_index+1]]
            num_of_coins=10000/exchange_coin1
            #exchanges.remove(exchange)
            differences=[]
            for each_exchange in ['kraken','kucoin','bitmex','bittrex','gemini']:
                exchange_index1=list(exchanges).index(each_exchange)
                exchange_coin2=group_coin[daily_returns.columns[exchange_index1+1]]
                difference=((abs(exchange_coin2-exchange_coin1)*num_of_coins)/abs(exchange_coin1)*num_of_coins).mean()
                differences=np.append(differences,difference)
            exchange_diff=pd.DataFrame({'exchanges':exchanges,exchange:differences})
            exchange_diff.set_index('exchanges',inplace=True)
            exchange_diff_all=pd.concat([exchange_diff_all,exchange_diff],axis=1)
        exchange_coin=pd.concat([exchange_coin,exchange_diff_all],axis=0)
        coin_name=np.append(coin_name,np.repeat(symbol,len(exchange_diff_all)))

    exchange_coin.insert(0,'coin',coin_name)
    return exchange_coin