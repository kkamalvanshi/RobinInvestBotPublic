import robin_stocks.robinhood as r
import pyotp
import sys
import requests
import json
import pandas as pd
import numpy as np
import datetime

#from sklearn.linear_model import RandomForestRegressor
from sklearn import linear_model
from sklearn.linear_model import RidgeCV, LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import KFold

totp = pyotp.TOTP('').now()
login = r.login('', '', mfa_code = totp)
print("Current OTP:", totp)
def quote(SYBL):
    sInfo = r.get_latest_price(SYBL)
    print(SYBL.upper() + ": $" + str(sInfo[0]))
    
def quote(SYBL):
    sInfo = r.get_latest_price(SYBL)
    print(SYBL.upper() + ": $" + str(sInfo[0]))
    
def historical(SYBL):
    time_int = 'day'
    time_span = '5year'

    hist = r.stocks.get_stock_historicals(SYBL, interval=time_int, span=time_span, bounds='regular', info=None)
    #sp_hist = r.stocks.get_stock_historicals('VOO', interval=time_int, span=time_span, bounds='regular', info=None) ##comparison with S&P500

    hour_dict = {'13':'09', '14':'10', '15':'11', '16':'12', '17':'01', '18':'02', '19':'03', '20':'04', '00':'00'}

    prev_price = 1
    #prev_sp_price = 1
    records = []
    
    for iter in hist:
        
        time = hour_dict[str(iter['begins_at'])[11:13]] + str(iter['begins_at'])[13:-4]

        #if time == '03:50' or time == '10:00':
        date = iter['begins_at'][:10]
        date = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[8:10]))

        #price comparison with s&p500
        open_price = float(iter['open_price'])
        close_price = float(iter['close_price'])
        high_price = float(iter['high_price'])
        low_price = float(iter['low_price'])
        volume = int(iter['volume'])

        #sp_open = float(sp_iter['open_price'])
        #sp_close = float(sp_iter['close_price'])

        #previous price to initial price is the initial price, so %change is 0 
        if prev_price == 1:
            prev_price = float(open_price)
            #prev_sp_price = float(sp_open)


        change = str(float((float(close_price) - prev_price)/prev_price)*100)
        #sp_change = str(float((float(sp_close) - prev_sp_price)/prev_sp_price)*100)

        change_deci = float(change)


        records.append([date, time, open_price, close_price, high_price, low_price, volume, change_deci])
        ##[date, time, price, change]

        #print(date + ' - ' + time + ' ---- $' + price + ' -- ' + change + ' %')
        prev_price = float(close_price)
        #prev_sp_price = float(sp_close)
    df_records = pd.DataFrame.from_records(records)
    df_records.columns=['date', 'time', 'open', 'close', 'high', 'low', 'vol', '%change']
    
    
    df_des = df_records.describe(percentiles=[0.00001, 0.0001, 0.001, 0.01, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25])
    
    #assuming starting with $20
    df_buy = pd.DataFrame()
    buy = []
    #df_buy.columns=['buy']
    
    #based on percentiles of change
    for change_deci in list(df_records['%change']):
        if change_deci<=df_des['%change']['25%'] and change_deci>df_des['%change']['22.5%']:
            buy.append(0.05)
        elif change_deci<=df_des['%change']['22.5%'] and change_deci>df_des['%change']['20%']:
            buy.append(0.075)
        elif change_deci<=df_des['%change']['20%'] and change_deci>df_des['%change']['17.5%']:
            buy.append(0.1)
        elif change_deci<=df_des['%change']['17.5%'] and change_deci>df_des['%change']['15%']:
            buy.append(0.125)
        elif change_deci<=df_des['%change']['15%'] and change_deci>df_des['%change']['12.5%']:
            buy.append(0.15)
        elif change_deci<=df_des['%change']['12.5%'] and change_deci>df_des['%change']['10%']:
            buy.append(0.175)
        elif change_deci<=df_des['%change']['7.5%'] and change_deci>df_des['%change']['5%']:
            buy.append(0.20)
        elif change_deci<=df_des['%change']['5%'] and change_deci>df_des['%change']['2.5%']:
            buy.append(0.225)
        elif change_deci<=df_des['%change']['2.5%'] and change_deci>df_des['%change']['1%']:
            buy.append(0.25)
        elif change_deci<=df_des['%change']['1%'] and change_deci>df_des['%change']['0.1%']:
            buy.append(0.275)
        elif change_deci<=df_des['%change']['0.1%'] and change_deci>df_des['%change']['0.01%']:
            buy.append(0.3)
        elif change_deci<=df_des['%change']['0.01%'] and change_deci>df_des['%change']['0.001%']:
            buy.append(0.325)
        else:
            buy.append(0.0)

    df_buy = pd.DataFrame(buy)
    df_buy.columns=['buy']
    
    df_records = pd.concat([df_records, df_buy], axis = 'columns')
    
    #df_records = df.append(today(SYBL).iloc[1])
    
    return df_records

def today(SYBL):
    week_day = r.stocks.get_stock_historicals(SYBL, interval='day', span='week', bounds='regular', info=None)
    week_5min = r.stocks.get_stock_historicals(SYBL, interval='5minute', span='week', bounds='regular', info=None)
    week_curr=[week_day[-1],week_5min[-1]]
    hour_dict = {'13':'09', '14':'10', '15':'11', '16':'12', '17':'01', '18':'02', '19':'03', '20':'04', '00':'00'}

    prev_price = 1
    records = []
    
    for iter in week_curr:
        
        time = hour_dict[str(iter['begins_at'])[11:13]] + str(iter['begins_at'])[13:-4]

        date = iter['begins_at'][:10]
        date = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[8:10]))

        #price comparison with s&p500
        open_price = float(iter['open_price'])
        close_price = float(iter['close_price'])
        high_price = float(iter['high_price'])
        low_price = float(iter['low_price'])
        volume = int(iter['volume'])

        #sp_open = float(sp_iter['open_price'])
        #sp_close = float(sp_iter['close_price'])

        #previous price to initial price is the initial price, so %change is 0 
        if prev_price == 1:
            prev_price = float(open_price)
            #prev_sp_price = float(sp_open)


        change = str(float((float(close_price) - prev_price)/prev_price)*100)
        #sp_change = str(float((float(sp_close) - prev_sp_price)/prev_sp_price)*100)

        change_deci = float(change)


        records.append([date, time, open_price, close_price, high_price, low_price, volume, change_deci])
        ##[date, time, price, change]

        #print(date + ' - ' + time + ' ---- $' + price + ' -- ' + change + ' %')
        prev_price = float(close_price)
        #prev_sp_price = float(sp_close)
    df_records = pd.DataFrame.from_records(records)
    df_records.columns=['date', 'time', 'open', 'close', 'high', 'low', 'vol', '%change']
    
    
    return df_records


df = historical('TSLA')
df.plot.line(x='date',y='close')
df.plot.line(x='date',y='buy')

#Creating MLM Model
model_rfr = RandomForestRegressor(n_estimators = 100)
X = df.drop(['buy', 'date', 'time'], axis = 'columns')
Y = df.buy

model_rfr.fit(X,Y)
model_rfr.score(X, Y)

#Predicting how much of TSLA to buy as of 6/3/2021
model_rfr.predict([[574.14, 572.83, 574.22, 572.1, 366042, -5.33613]])

#Split scrambled version of dataset into training and testing models
#Create model looking strictly at the past month
##research trends in VOO/S&P500
##Implement invest Method
