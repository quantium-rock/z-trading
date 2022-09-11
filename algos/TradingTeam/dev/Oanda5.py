from oauth2client.service_account import ServiceAccountCredentials as SAC
import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import statistics as stat
import gspread as gs
from datetime import datetime as dt

OA = { 'Token': 'ea74153c2aba5b6e58714d57b3601602-7669b039c81edcc9b1ec2e4c8fadf2fa',
       'ID': '101-004-9922005-003' }

def GSapi(GSname,GSsheet):
    scope = ["https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]
    credentials = SAC.from_json_keyfile_name('C:\ZorroBeta\Strategy\Python\GoogleSheet\GoogleSheet-b90941c49358.json',scope)
    ga = gs.authorize(credentials)
    return ga.open(GSname).worksheet(GSsheet)

def Oanda_Candles(Symbol,params):
    r = instruments.InstrumentsCandles(instrument=Symbol,params=params)
    rv = api.request(r)
    df = pd.DataFrame(r.response['candles'])
    Len = len(df); t, o, h, l, c, r, v = [], [], [], [], [], [], []
    for i in range(Len):
        if df['complete'][i]:
            t.append(dt.strptime(df['time'][i][:19],'%Y-%m-%dT%H:%M:%S'))
            o.append(float(df['mid'][i]['o']))
            h.append(float(df['mid'][i]['h']))
            l.append(float(df['mid'][i]['l']))
            c.append(float(df['mid'][i]['c']))
            r.append(float(df['mid'][i]['c'])/float(df['mid'][i]['o'])-1)
            v.append(int(df['volume'][i]))
    df = pd.DataFrame({'DateTime':t,'Open':o,'High':h,'Low':l,'Close':c,'Return':r,'Volume':v})
    df = df.set_index('DateTime')
    return df

api = API(access_token=OA['Token'])
g = GSapi('OandaEurope','Trend')

params = {
    'count': '1440',
    'granularity': 'H1'
}
Symbols = ['AU200_AUD','CN50_USD','EU50_EUR','FR40_EUR','DE30_EUR','HK33_HKD','IN50_USD','JP225_USD','NL25_EUR','SG30_SGD','TWIX_USD','UK100_GBP','NAS100_USD','US2000_USD','SPX500_USD','US30_USD','DE10YB_EUR','UK10YB_GBP','USB10Y_USD','USB02Y_USD','USB05Y_USD','USB30Y_USD','BCO_USD','WTICO_USD','NATGAS_USD','CORN_USD','SOYBN_USD','SUGAR_USD','WHEAT_USD','XCU_USD','XPT_USD','XPD_USD','XAU_USD','XAG_USD','XAU_AUD','XAU_CAD','XAU_CHF','XAU_EUR','XAU_GBP','XAU_HKD','XAU_JPY','XAU_NZD','XAU_SGD','XAU_XAG','XAG_AUD','XAG_CAD','XAG_CHF','XAG_EUR','XAG_GBP','XAG_HKD','XAG_JPY','XAG_NZD','XAG_SGD','AUD_USD','EUR_USD','GBP_USD','NZD_USD','USD_CAD','USD_CHF','USD_HKD','USD_JPY','USD_SGD','AUD_CAD','AUD_CHF','AUD_HKD','AUD_JPY','AUD_NZD','AUD_SGD','CAD_CHF','CAD_HKD','CAD_JPY','CAD_SGD','CHF_HKD','CHF_JPY','EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP','EUR_HKD','EUR_JPY','EUR_NZD','EUR_SGD','GBP_AUD','GBP_CAD','GBP_CHF','GBP_HKD','GBP_JPY','GBP_NZD','GBP_SGD','HKD_JPY','NZD_CAD','NZD_CHF','NZD_HKD','NZD_JPY','NZD_SGD','SGD_CHF','SGD_HKD','SGD_JPY','EUR_DKK','EUR_NOK','EUR_SEK','USD_DKK','USD_NOK','USD_SEK','CHF_ZAR','EUR_CZK','EUR_HUF','EUR_PLN','EUR_TRY','EUR_ZAR','GBP_PLN','GBP_ZAR','TRY_JPY','USD_CNH','USD_CZK','USD_HUF','USD_INR','USD_MXN','USD_PLN','USD_SAR','USD_THB','USD_TRY','USD_ZAR','ZAR_JPY']
GScols = ['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y']

for row in range(20,40):
    df = Oanda_Candles(Symbols[row],params)
    df['Hour'] = df.index.hour
    df = df.set_index('Hour')
    Len = len(df); Dir = []
    for i in range(Len):
        x = 0
        if i < Len-1:
            if ( df.iloc[i+1]['Return'] > 0 and df.iloc[i]['Return'] > 0 ) or ( df.iloc[i+1]['Return'] < 0 and df.iloc[i]['Return'] < 0 ):
                x = 1
            elif ( df.iloc[i+1]['Return'] > 0 and df.iloc[i]['Return'] < 0 ) or ( df.iloc[i+1]['Return'] < 0 and df.iloc[i]['Return'] > 0 ):
                x = -1
        Dir.append(x)
    df['Dir'] = Dir
    h = 0
    for col in GScols:
        cell = col + str(row+3)
        if sum(df.index == h) < 3:
            GSupdate = g.update_acell(cell,'N/A')
        else:
            GSupdate = g.update_acell(cell,stat.mean(df['Dir'][h]))
        h += 1

