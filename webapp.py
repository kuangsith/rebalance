import pandas as pd
import datetime
import get_price_binanace
import streamlit as st

st.header('Rebalancing')

coinlist = ['BTC','ETH','SOL','BNB','']
asset1 = st.selectbox()
asset2 = st.selectbox()

ticker1 = 'ADA'
ticker2 = 'SOL'

year = 2022
month = 1
day = 1

timestart = int(datetime.datetime(year,month,day,tzinfo=datetime.timezone.utc).timestamp())*1000

df1 = get_price_binanace.getprice_days(ticker1,timestart)
df1['datetime'] = pd.to_datetime(df1['datetime'],utc=True)
df1['price'] = pd.to_numeric(df1['price'])
df1=df1.rename(columns={'price':ticker1})

df2 = get_price_binanace.getprice_days(ticker2,timestart)
df2['datetime'] = pd.to_datetime(df2['datetime'],utc=True)
df2['price'] = pd.to_numeric(df2['price'])
df2=df2.rename(columns={'price':ticker2})

# print(df1.info())
# print(df2.head())

df = pd.merge(df1,df2,on='datetime')

initcap = 100.00

df[f'future {ticker1}'] = df[ticker1].shift(-1)
df[f'future {ticker2}'] = df[ticker2].shift(-1)

df[f'return {ticker1}'] = (df[f"future {ticker1}"] - df[ticker1])/df[ticker1]
df[f'return {ticker2}'] = (df[f"future {ticker2}"] - df[ticker2])/df[ticker2]

df = df.drop(f'future {ticker1}', axis=1)
df = df.drop(f'future {ticker2}', axis=1)

df[f'Capital - {ticker1}'] = 0.00

df.loc[0,f'Capital - {ticker1}'] = initcap

for i,row in df.iloc[1:].iterrows():
    yesterdaycap = df.loc[i-1,f'Capital - {ticker1}']
    yesterdayreturn = df.loc[i-1,f'return {ticker1}']
    df.loc[i,f'Capital - {ticker1}'] = yesterdaycap*(1+yesterdayreturn)


df.loc[0,f'Capital - {ticker2}'] = initcap

for i,row in df.iloc[1:].iterrows():
    yesterdaycap = df.loc[i-1,f'Capital - {ticker2}']
    yesterdayreturn = df.loc[i-1,f'return {ticker2}']
    df.loc[i,f'Capital - {ticker2}'] = yesterdaycap*(1+yesterdayreturn)
    
ratio = 0.5
fee = 0.0
acceptablerange = 0.05 #This will rebalance if the ratio if off by >= aceptablerange

df[f'portion {ticker1}'] = 0.0
df.loc[0,f'portion {ticker1}'] = ratio*initcap
df[f'portion {ticker2}'] = 0.0
df.loc[0,f'portion {ticker2}'] = (1-ratio)*initcap

df['Total Cap'] = 0.0
df.loc[0,'Total Cap'] = initcap
df['Rebalance?'] = False

df['ratio'] = ratio

df[f'portion {ticker1} - reb'] = df[f'portion {ticker1}']
df[f'portion {ticker2} - reb'] = df[f'portion {ticker2}']

for i,row in df.iloc[1:].iterrows():
    df.loc[i,f'portion {ticker1}'] = df.loc[i-1,f'portion {ticker1} - reb']*(1+df.loc[i-1,f'return {ticker1}'])
    df.loc[i,f'portion {ticker2}'] = df.loc[i-1,f'portion {ticker2} - reb']*(1+df.loc[i-1,f'return {ticker2}'])
    df.loc[i,'Total Cap'] = df.loc[i,f'portion {ticker1}'] + df.loc[i,f'portion {ticker2}']
    df.loc[i,'ratio'] = df.loc[i,f'portion {ticker1}']/df.loc[i,'Total Cap']

    if abs(df.loc[i,f'portion {ticker1}']/df.loc[i,'Total Cap']-ratio) >= acceptablerange:
        df.loc[i,'Rebalance?'] = True
        df.loc[i,f'portion {ticker1} - reb'] = ratio*df.loc[i,'Total Cap']
        df.loc[i,f'portion {ticker2} - reb'] = df.loc[i,'Total Cap'] - df.loc[i,f'portion {ticker1} - reb']
    else:
        df.loc[i,f'portion {ticker1} - reb'] = df.loc[i,f'portion {ticker1}']
        df.loc[i,f'portion {ticker2} - reb'] = df.loc[i,f'portion {ticker2}']
