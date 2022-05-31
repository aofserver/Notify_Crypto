




# listnoti = []
# for i in range(10):
#   data = cg.get_coins_markets(vs_currency='usd', per_page=250, price_change_percentage='24h', page=i)
#   df = pd.DataFrame(data)
#   list_name = ['btc','eth','bnb','luna','doge','sol','dot','shib','ust']
#   df = df[df.symbol.isin(list_name)]
#   df['ath_change_percentage']
#   df = df.loc[(abs(df['ath_change_percentage']) >= 78.6) & (abs(df['ath_change_percentage']) <= 88.7)]
#   for i in range(len(df.index)):
#     data = {"symbol":df.iloc[i].symbol,"ath_change_percentage":df.iloc[i].ath_change_percentage,"current_price":df.iloc[i].current_price}
#     listnoti.append(data)
#     print(df.iloc[i].symbol,df.iloc[i].ath_change_percentage,df.iloc[i].current_price)
# print(len(listnoti))


import requests
import numpy as np
import pandas as pd
from datetime import datetime
from pycoingecko import CoinGeckoAPI

from Database import SQL
from pydantic import BaseModel
from fastapi import File, Form, UploadFile, APIRouter, Request


cg = CoinGeckoAPI()
router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
    responses={404: {"message": "Not found"}}
)

def ValidateUser(id,token):
    cmd = "SELECT tokenlinenoti FROM userinfo WHERE id={};".format(id)
    res = SQL.Query(cmd)
    if len(res) == 0:
        return False
    return res[0]['tokenlinenoti'] == token

@router.get("/listcoin") 
async def Listcoin(request: Request):
    return cg.get_coins_list()


class info(BaseModel):
    listidx: list
@router.post("/info")
async def GetPrice(request: Request, info:info):
    data = info.dict()
    df = cg.get_coins_markets(vs_currency='usd', ids=data['listidx'], per_page=250, price_change_percentage='24h', page=1)
    list_data = []
    for i in df:
        list_data.append({
                            "symbol": i['symbol'],
                            "coin": i['id'],
                            "price": i['current_price'],
                            "ath_change": i['ath_change_percentage'],
                            "market_cap": i['market_cap'],
                        })
    return list_data




class ath(BaseModel):
    more: float
    less: float
@router.get("/ath")
async def ChangeATH(request: Request, ath:ath):
    list_data = []
    data = ath.dict()
    for i in range(10):
        data_coin = cg.get_coins_markets(vs_currency='usd', per_page=250, price_change_percentage='24h', page=i)
        df = pd.DataFrame(data_coin)
        df = df.loc[(abs(df['ath_change_percentage']) >= data['more']) & (abs(df['ath_change_percentage']) <= data['less'])]
        for i in range(len(df.index)):
            list_data.append({
                                "symbol":df.iloc[i].symbol,
                                "market_cap": df.iloc[i].market_cap,
                                "ath_change_percentage":df.iloc[i].ath_change_percentage,
                                "current_price":df.iloc[i].current_price
                            })
    return list_data