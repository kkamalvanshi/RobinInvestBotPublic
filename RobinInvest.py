import robin_stocks.robinhood as r
import pyotp
import sys
import requests
import json
import pandas as pd
import datetime

totp = pyotp.TOTP('').now()
login = r.login('', '', mfa_code = totp)
print("Current OTP:", totp)

final_records = pd.DataFrame()

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
        ##sp_price = str(sp_iter['open_price'])

        #previous price to initial price is the initial price, so %change is 0 
        if prev_price == 1:
            prev_price = float(open_price)
            #prev_sp_price = float(sp_price)

        
        change = str(float((float(close_price) - prev_price)/prev_price)*100)
        #sp_change = str(float((float(sp_price) - prev_sp_price)/prev_sp_price)*100)

        change_deci = float(change)
        
        #assuming starting with $20
        buy_per = 0
        if change_deci<=-0.75 and change_deci>-1.25:
            buy_per = 0.05
        elif change_deci<=-1.25 and change_deci>-1.75:
            buy_per = 0.1
        elif change_deci<=-1.75 and change_deci>-2.5:
            buy_per = 0.15
        elif change_deci<=-2.5 and change_deci>-5.0:
            buy_per = 0.2
        elif change_deci<=-5.0 and change_deci>-7.5:
            buy_per = 0.25
        elif change_deci<=-7.5:
            buy_per = 0.30
            

        records.append([date, open_price, close_price, high_price, low_price, volume, time, change_deci, buy_per])
        ##[date, time, price, change]

        #print(date + ' - ' + time + ' ---- $' + price + ' -- ' + change + ' %')
        prev_price = float(close_price)
        #prev_sp_price = float(sp_price)
    df_records = pd.DataFrame.from_records(records)
    df_records.columns=['date', 'open', 'close', 'high', 'low', 'vol', 'time', '%change', 'buy']
    print (df_records)


historical('SQ')

##fix int to day
##research trends in VOO/S&P500
##Implement invest Method
