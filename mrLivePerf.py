# -*- coding: utf-8 -*-
"""
Created on Sun Aug 29 12:16:56 2021

@author: sai.pydisetty
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import requests,json
from datetime import datetime

pnl_url = 'https://pythonbucketbh.s3.ap-south-1.amazonaws.com/allPnl.json'

pnl_data=requests.get(pnl_url)
pnl_df_t=pd.DataFrame.from_dict(json.loads(pnl_data.text))
pnl_df=pnl_df_t.T
pnl_df['ALL']=pnl_df['pnl']+pnl_df['intra_pnl']+pnl_df['mr_pnl']
pnl_df.rename({'pnl':'BNFStraddle', 'intra_pnl':'IntradayTrend', 'mr_pnl':'MeanReversion'}, axis=1,inplace=True)
option = 'ALL'

st.title("**♟**PERFORMANCE**♟**")
option = st.selectbox(
    'Select Strategy',
    ('ALL', 'BNFStraddle', 'MeanReversion', 'IntradayTrend'))

strategyCapitalDic={"BNFStraddle":200000,"MeanReversion":100000,"IntradayTrend":50000, "ALL":350000}

botCapital=strategyCapitalDic[option]
strat_pnl_Df=pnl_df[[option]]
strat_pnl_Df.dropna(inplace=True)
strat_df=strat_pnl_Df

##PNL plot
strat_df['pdTime']=pd.to_datetime(strat_df.index,format="%Y-%m-%d")
strat_df.sort_values('pdTime',inplace=True)
#strat_df[option]=(botCapital/100)*strat_df[option].astype(float)
strat_df["Time"]=strat_df.index
strat_df['PNL']=strat_df[option]
strat_df['cum_pnl']=strat_df[option].cumsum()


##DRAWDOWN
drawdown_df=strat_df.copy()
drawdown_df.reset_index(drop=True,inplace=True)
drawdown_df['max_value_so_far']=drawdown_df['cum_pnl'].cummax()
drawdown_df['drawdown']=drawdown_df['cum_pnl']-drawdown_df['max_value_so_far']
##Strategy statistics
stats_Df=pd.DataFrame(columns=["Total Days","Winning Days","Losing Days","Win Ratio(%)","Max Profit","Max Loss","Max Drawdown","Average Profit on Win Days","Average Profit on loss days","Average Profit Per day","Net profit","net Returns (%)"])
total_days=len(strat_df)
win_df=strat_df[strat_df[option].astype('float')>0]
lose_df=strat_df[strat_df[option].astype('float')<0]
noTrade_df=strat_df[strat_df[option].astype('float')==0]

win_days=len(win_df)
lose_days=len(lose_df)

win_ratio=win_days*1.0/lose_days
max_profit=strat_df[option].max()
max_loss=strat_df[option].min()

max_drawdown=0
win_average_profit=win_df[option].sum()/win_days
loss_average_profit=lose_df[option].sum()/lose_days

total_profit=strat_df[option].sum()
average_profit=total_profit/total_days

net_returns= round(strat_df['cum_pnl'].iloc[-1]*100/botCapital,2)

results_row=[total_days,win_days,lose_days,win_ratio,max_profit,max_loss,max_drawdown,win_average_profit,loss_average_profit,average_profit,total_profit,net_returns]

results_row=[results_row[i] if i<3 else round(results_row[i],2) for i in range(len(results_row)) ]
stats_Df.loc[0,:]=results_row
t_stats_Df=stats_Df.T
t_stats_Df.rename(columns={0:''},inplace=True)
fig=px.line(strat_df, x="Time", y='cum_pnl', title=option+' PNL',width=800, height=400)
dd_fig=px.line(drawdown_df,x="Time",y="drawdown", title=option+' PNL',width=800, height=400)

strat_df['month']=strat_df['pdTime'].apply(lambda x:x.strftime('%b,%Y'))

month_groups=strat_df.groupby('month',sort=False)['PNL'].sum()


##last 30 days pnl
strat_df=strat_df.reindex(strat_df.index[::-1])


st.write("**LIVE PERFORMANCE OF "+option+"**")
st.write("**[Capital used is "+str(botCapital)+"]**")
st.write("Net ROI : "+str(results_row[-1])+"%")


st.write("**Statistics**")
st.table(t_stats_Df)
st.write("**PNL Curve**")
st.plotly_chart(fig)
st.write("**Drawdown Curve**")
st.plotly_chart(dd_fig)
st.write("**Month-wise PNL**")
st.table(month_groups)
st.write("**Date-wise PNL (Last 30 Days)**")
st.table(strat_df['PNL'][:30])
