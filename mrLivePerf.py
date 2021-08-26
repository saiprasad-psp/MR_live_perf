# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 14:23:38 2021

@author: sai.pydisetty
"""

import json
import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import matplotlib.image as mpimg 


#api_url_mr = "https://e91pez1xi8.execute-api.ap-south-1.amazonaws.com/pnl?"
api_url_mr = "https://pythonbucketbh.s3.ap-south-1.amazonaws.com/pnl.json"
payload = {}
headers= {}
response_mr = requests.request("GET", api_url_mr, headers=headers, data = payload)
data = json.loads(response_mr.text)['data']

#Dataframe for daily returns
df = pd.DataFrame(data)
df = df.rename(columns = {'_id':'Date'})
#df = df.set_index('_id')
df = df.iloc[::-1]
df['pnl'] = round(df['pnl'],1)
df['cum_pnl'] = df['pnl'].cumsum()
net_roi = round(df['cum_pnl'].iloc[-1]*100/100000,2)
df['month'] = pd.DatetimeIndex(df['Date']).month 
df['year'] = pd.DatetimeIndex(df['Date']).year
df['month'] = pd.to_datetime(df['month'], format='%m').dt.month_name().str.slice(stop=3)
df['month_year'] = (df['month'] + df['year'].astype(str)).str.slice(stop = 7)

#Dataframe for monthly returns
df1 = df.groupby(['month_year'],sort = False).sum()
df1['% Returns'] = round(df1['pnl']*100/100000,2)
df1 = df1.reset_index()

fig_pnl = px.line(df, x='Date', y='cum_pnl',width = 800,height = 500)

#Remove the None element
if df.Date[0]:
    df = df[1:]

#Create Drawdown column
df['drawdown'] = 0
for i in range(0,df.shape[0]):
    
    if i == 0:
        if df['pnl'].iloc[i] > 0:
            df['drawdown'].iloc[i] = 0
        else:
            df['drawdown'].iloc[i] = df['pnl'].iloc[i]
    else:
        if df['pnl'].iloc[i] + df['drawdown'].iloc[i-1] > 0:
            df['drawdown'].iloc[i] = 0
        else:
            df['drawdown'].iloc[i] = df['pnl'].iloc[i] + df['drawdown'].iloc[i-1]

fig_dd = px.line(df, x='Date', y='drawdown',width = 800,height = 500)

#Statistics
total_days = len(df)
winning_days = (df['pnl'] > 0).sum()
losing_days = (df['pnl'] < 0).sum()
null_days = (df['pnl'] == 0).sum()

win_ratio = round((df['pnl'] > 0).sum()*100/len(df),2)
max_profit = round(df['pnl'].max(),2)
max_loss = round(df['pnl'].min(),2)
max_drawdown = round(df['drawdown'].min(),2)
avg_profit_on_win_days = df[df['pnl'] > 0]['pnl'].sum()/len(df[df['pnl'] > 0])
avg_loss_on_loss_days = df[df['pnl'] < 0]['pnl'].sum()/len(df[df['pnl'] < 0])
avg_profit_per_day = df['pnl'].sum()/len(df)
expectancy = round(((avg_profit_on_win_days*win_ratio + avg_loss_on_loss_days*(100 - win_ratio))*0.01)/(-avg_loss_on_loss_days),8)
net_profit = round(df['cum_pnl'].iloc[-1],2)
net_returns = round(net_roi,2)

KPI = {'Total days':total_days,'Winning days':winning_days,'Losing days':losing_days,'Null days(orders untriggered)':null_days,'Win Ratio (%)':win_ratio, 'Max Profit':max_profit,'Max Loss':max_loss,'Max Drawdown':max_drawdown,'Average Profit on win days': avg_profit_on_win_days, 'Average Loss on loss days': avg_loss_on_loss_days, 'Average Profit per day': avg_profit_per_day,'Expectancy': expectancy,'Net Profit':net_profit, 'Net Returns (%)': net_returns}
strategy_stats = pd.DataFrame(KPI.values(),index = KPI.keys(),columns = [' '])

#Content and charts on the webapp
st.markdown("<h1 style='text-align: center; color: black;'>Live Performance of Mean Reversion Strategy</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: right; color: black;'>[Capital used is 1 lac with 3x leverage (we do not recommend to use more than 3x margin)]</h4>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: right; color: black;'>[Daily Maximum Risk:- 9000]</h4>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: right; color: black;'>[Start Date :- 26 Aug, 2020]</h4>", unsafe_allow_html=True)
#link = '[Sign up for the Free Trial of this bot](https://forms.gle/sGAjc37RHK4VM7bq9)'
#st.markdown(link, unsafe_allow_html=True)
#Percentage ROI
st.header('Net ROI: '+ str(net_roi) + '%')

#Statistics
st.header('Strategy Statistics')
st.table(strategy_stats)

#PNL curve
st.header('PNL Curve')
st.plotly_chart(fig_pnl)

#Drawdown curve
st.header('Drawdown Curve')
st.plotly_chart(fig_dd)

#Month-wise PNL
st.header('Month-wise PNL')
st.table(df1[['month_year','% Returns']])

#Date-wise PNL
st.header('Date-wise PNL (Last 30 days)')
st.table(df[['Date','pnl']][-30:].astype('object'))


# HtmlFile = open(“index.html”, ‘r’, encoding=‘utf-8’)
# source_code = HtmlFile.read()
# print(source_code)
# components.html(source_code, height=600)
