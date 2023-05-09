import requests
import json
import pandas as pd
import datetime
import time



def stamptotime(stamp):
    stamp = stamp/1000
    t = datetime.datetime.utcfromtimestamp(stamp)
    return t.strftime("%Y-%m-%d %H:%M:%S")


def getprice(ticker,timestamp):

    # Define the parameters for the API request
    symbol = f'{ticker}USDT'      # Trading pair symbol
    interval = '1s'        # Kline interval (1 day)
    start_time = timestamp    # Start time in milliseconds (July 1, 2020)
    end_time = timestamp      # End time in milliseconds (July 1, 2021)
    limit = '2'         # Number of Klines to retrieve at once

    # Define the URL for the API request
    
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit={limit}'
    try:
        response = requests.get(url)
        # check for rate-limiting response codes
        if response.status_code == 429:
            # wait and retry after a certain amount of time
            retry_after = int(response.headers.get('Retry-After'))
            time.sleep(retry_after)
            return getprice(ticker,timestamp)
        else:
            klines = json.loads(response.text)
            if len(klines) == 0:
                return float("nan")
            else:
                return float(klines[0][1])
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
def getprice_days(ticker,timestamp):
    # get daily price for max number of days
    # Define the parameters for the API request
    symbol = f'{ticker}USDT'      # Trading pair symbol
    interval = '1d'        # Kline interval (1 day)
    start_time = timestamp    
    end_time = timestamp + 1000*60*60*24*1000
    limit = '1000'         # Number of Klines to retrieve at once

    # Define the URL for the API request
    
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit={limit}'
    try:
        response = requests.get(url)
        # check for rate-limiting response codes
        if response.status_code == 429:
            # wait and retry after a certain amount of time
            retry_after = int(response.headers.get('Retry-After'))
            time.sleep(retry_after)
            return getprice(ticker,timestamp)
        else:
            klines = json.loads(response.text)
            if len(klines) == 0:
                return float("nan")
            else:
                numcol = len(list(klines)[0])
                p = pd.DataFrame(klines,index=list(range(numcol)))
                p = p[[0,1]]
                p = p.rename(columns={0:'datetime',1:'price'})
                p['datetime'] = p['datetime'].apply(stamptotime)
                return p
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


# Print the results
# print(df.head())


def roundoutmicrosecond(mydate):
    return mydate.replace(microsecond=0)


# start = int(datetime.datetime(2021,12,31,12,0,0,tzinfo=datetime.timezone.utc).timestamp())*1000

# ticker = "SOL"
# mytime = 1640976066000
# p = getprice_days(ticker,mytime)
# print(type(p))

# print(p)





