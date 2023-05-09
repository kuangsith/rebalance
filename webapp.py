import pandas as pd
import datetime
import get_price_binanace
import streamlit as st
import numpy

if 'ticker1' not in st.session_state:
    st.session_state.ticker1 = 'BTC'
if 'ticker2' not in st.session_state:
    st.session_state.ticker2 = 'ETH'
if 'ratio' not in st.session_state:
    st.session_state.ratio = 0.5
if 'acceptablerange' not in st.session_state:
    st.session_state.acceptablerange = 0.05

st.header('Rebalancing')


with st.expander("Setting"):
    col1, col2 = st.columns(2)

    coinlist = ['BTC','ETH','SOL','BNB','ADA']

    with col1:
        ticker1_temp = st.selectbox('Asset #1',coinlist)

    with col2:
        ticker2_temp = st.selectbox('Asset #2',coinlist)

    kol1, kol2, kol3 = st.columns(3)


    with kol1:
        ratio_temp = st.slider('Ratio of asset1 to total captal:',min_value=0.1,max_value=0.9,value=0.5)

    with kol2:
        acceptable_temp = st.slider('Percentage off to rebalance:', min_value=0.00, max_value = 0.2,value=0.05)

    with kol3:
        update = st.button('Update')



year = 2022
month = 1
day = 1

#defining all parameters
ticker1 = st.session_state.ticker1
ticker2 = st.session_state.ticker2
ratio = st.session_state.ratio
acceptablerange = st.session_state.acceptablerange

timestart = int(datetime.datetime(year,month,day,tzinfo=datetime.timezone.utc).timestamp())*1000

# st.text(get_price_binanace.getprice_days(ticker1,timestart))

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

fee = 0.0

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

df = df.dropna()

## Displaying key performance indicator

dfperf = pd.DataFrame([],columns= ['Investment','Profit','Sharpe ratio','Max Drawdown'])

investment1 = ticker1
profit1 = get_price_binanace.profit(df[f'Capital - {ticker1}'])
sharpe1 = get_price_binanace.sharpe(df[f'Capital - {ticker1}'])
mdd1 = get_price_binanace.maxdrawdown(df[f'Capital - {ticker1}'])
dat1 = [investment1,profit1,sharpe1,mdd1]

investment2 = ticker2
profit2 = get_price_binanace.profit(df[f'Capital - {ticker2}'])
sharpe2 = get_price_binanace.sharpe(df[f'Capital - {ticker2}'])
mdd2 = get_price_binanace.maxdrawdown(df[f'Capital - {ticker2}'])
dat2 = [investment2,profit2,sharpe2,mdd2]

investment3 = 'Rebalancing'
profit3 = get_price_binanace.profit(df['Total Cap'])
sharpe3 = get_price_binanace.sharpe(df['Total Cap'])
mdd3 = get_price_binanace.maxdrawdown(df['Total Cap'])
dat3 = [investment3,profit3,sharpe3,mdd3]

dfperf = pd.DataFrame([dat1,dat2,dat3],columns= ['Investment','Profit','Sharpe ratio','Max Drawdown'])

st.dataframe(dfperf)


## Displaying data

st.write(f"Rebalacing with {int(ratio*100)}% on {ticker1} and {int((1-ratio)*100)}% on {ticker2}.")

st.line_chart(data=df[[f'Capital - {ticker1}',f'Capital - {ticker2}','Total Cap']])

st.write('Full dataframe:')

st.dataframe(df)



if update:
    st.session_state.ticker1 = ticker1_temp
    st.session_state.ticker2 = ticker2_temp
    st.session_state.ratio = ratio_temp
    st.session_state.acceptablerange = acceptable_temp
    st.experimental_rerun()