import time
import datetime
import requests
from Database import SQL

list_token = {}
setbuff = 2
notify = []

typecoin = {
            "OKX":[],
            "BINANCE":[]
           }


def LineNotify(msg,token):
  url = 'https://notify-api.line.me/api/notify'
  headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer ' + token}
  r = requests.post(url, headers=headers, data = {'message':msg})
  r = r.json()
  if r["status"] == 401:
    SQL.RUN("DELETE FROM notify WHERE token='{}'".format(token))


def LineNotifyBroadcast(coin,exchange):
    msg = "/n⚠ {} กำลังจะเปิดเทรดใน {}!".format(coin,exchange)
    for i in SQL.Query("SELECT tokenlinenoti FROM userinfo;"):
        LineNotify(msg,i['tokenlinenoti'])


def GetNotify():
    global notify
    notify = SQL.Query("SELECT notify.id,exchange.name AS exchange,notify.coin,typenotify.id as typenotify,notify.price,notify.cntnotify,userinfo.tokenlinenoti AS token,notify.status,notify.create_timestamp,notify.update_timestamp FROM notify INNER JOIN exchange ON notify.exchange_id=exchange.id JOIN typenotify ON notify.typenotify=typenotify.id JOIN userinfo ON notify.userinfo_id=userinfo.id ORDER BY notify.id")



def GetTypeCoin():
    global typecoin
    for i in SQL.Query("SELECT * FROM typecoin WHERE exchange=1;"): #OKX
        if not(i['coin'] in typecoin["OKX"]):
            typecoin["OKX"].append(i['coin'])

    for i in SQL.Query("SELECT * FROM typecoin WHERE exchange=2;"): #BINANCE
        if not(i['coin'] in typecoin["BINANCE"]):
            typecoin["BINANCE"].append(i['coin'])



def GetPriceOKX():
    url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
    response = requests.request("GET", url, headers={}, data={})
    data = response.json()
    for i in data["data"]:
        try:
            if not(i['instId'] in typecoin["OKX"]):
                print(i['instId'])
                typecoin["OKX"].append(i['instId'])
                SQL.RUN("INSERT INTO typecoin (exchange, coin) VALUES (1, '{}');".format(i['instId']))
                LineNotifyBroadcast(i['instId'],"OKX")

            if len(list_token["OKX"][i["instId"]]) < setbuff:
                list_token["OKX"][i["instId"]].append(i["last"]) 
            else:
                list_token["OKX"][i["instId"]].pop(0)
                list_token["OKX"][i["instId"]].append(i["last"])
        except:
            if not "OKX" in list_token.keys():
                list_token["OKX"] = {}
            list_token["OKX"][i["instId"]] = [i["last"]]


def GetPriceBinance():
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.request("GET", url, headers={}, data={})
    data = response.json()
    for i in data:
        try:
            if not(i['symbol'] in typecoin["BINANCE"]):
                print(i['symbol'])
                typecoin["BINANCE"].append(i['symbol'])
                SQL.RUN("INSERT INTO typecoin (exchange, coin) VALUES (2, '{}');".format(i['symbol']))
                LineNotifyBroadcast(i['symbol'],"BINANCE")

            if len(list_token["BINANCE"][i["symbol"]]) < setbuff:
                list_token["BINANCE"][i["symbol"]].append(i["price"]) 
            else:
                list_token["BINANCE"][i["symbol"]].pop(0)
                list_token["BINANCE"][i["symbol"]].append(i["price"])
        except:
            if not "BINANCE" in list_token.keys():
                list_token["BINANCE"] = {}
            list_token["BINANCE"][i["symbol"]] = [i["price"]]


def GetPriceALL():
    GetTypeCoin()
    GetPriceOKX()
    GetPriceBinance()
    ConditionNotify()


#################
# typenotify = 1    มากกว่าราคาที่ตั้งไว้ เตือนหนึ่งครั้ง
# typenotify = 2    น้อยกว่าราคาที่ตั้งไว้ เตือนหนึ่งครั้ง
# typenotify = 3    มากกว่าราคาที่ตั้งไว้ เตือนทุกครั้ง
# typenotify = 4    น้อยกว่าราคาที่ตั้งไว้ เตือนทุกครั้ง
#################
def ConditionNotify():
    GetNotify()
    print("============================")
    for i in notify:
        print(i['exchange'],i['coin'],i['typenotify'],i['price'],i['cntnotify'])
        current_price = float(list_token[i['exchange']][i['coin']][-1])
        set_price = float(i['price'])
        difftime = (datetime.datetime.now() - datetime.datetime.fromisoformat(str(i['update_timestamp']))).seconds
        
        if current_price >= set_price and i['typenotify'] == 1 and not(i['status']) and i['cntnotify'] == 0:
            i['cntnotify'] += 1
            i['status'] = int(not(i['status']))
            cmd = "UPDATE notify SET cntnotify='{cntnotify}',status='{status}' WHERE id={id}".format(cntnotify=i['cntnotify'],status=i['status'],id=i['id'])
            res = SQL.RUN(cmd)
            if res:
                msg = "\n{exchange} : {coin} ↗ ราคาสูงกว่า {set_price}\nราคาปัจจุบัน {current_price}".format(exchange=i['exchange'],coin=i['coin'],set_price=str(set_price),current_price=str(current_price))
                LineNotify(msg,i['token'])

        if current_price <= set_price and i['typenotify'] == 2 and not(i['status']) and i['cntnotify'] == 0:
            i['cntnotify'] += 1
            i['status'] = int(not(i['status']))
            cmd = "UPDATE notify SET cntnotify='{cntnotify}',status='{status}' WHERE id={id}".format(cntnotify=i['cntnotify'],status=i['status'],id=i['id'])
            res = SQL.RUN(cmd)
            if res:
                msg = "\n{exchange} : {coin} ↘ ราคาต่ำกว่า {set_price}\nราคาปัจจุบัน {current_price}".format(exchange=i['exchange'],coin=i['coin'],set_price=str(set_price),current_price=str(current_price))
                LineNotify(msg,i['token'])

        

        if current_price >= set_price and i['typenotify'] == 3 and not(i['status']) and difftime >= 30:
            i['cntnotify'] += 1
            i['status'] = int(not(i['status']))
            cmd = "UPDATE notify SET cntnotify='{cntnotify}',status='{status}' WHERE id={id}".format(cntnotify=i['cntnotify'],status=i['status'],id=i['id'])
            res = SQL.RUN(cmd)
            if res:
                msg = "\n{exchange} : {coin} ↗ ราคาสูงกว่า {set_price}\nราคาปัจจุบัน {current_price}".format(exchange=i['exchange'],coin=i['coin'],set_price=str(set_price),current_price=str(current_price))
                LineNotify(msg,i['token'])
        elif current_price < set_price and i['typenotify'] == 3 and i['status']:
            i['status'] = 0
            cmd = "UPDATE notify SET status='{status}' WHERE id={id}".format(status=i['status'],id=i['id'])
            res = SQL.RUN(cmd)



        if current_price <= set_price and i['typenotify'] == 4 and not(i['status']) and difftime >= 30:
            i['cntnotify'] += 1
            i['status'] = int(not(i['status']))
            cmd = "UPDATE notify SET cntnotify='{cntnotify}',status='{status}' WHERE id={id}".format(cntnotify=i['cntnotify'],status=i['status'],id=i['id'])
            res = SQL.RUN(cmd)
            if res:
                msg = "\n{exchange} : {coin} ↘ ราคาต่ำกว่า {set_price}\nราคาปัจจุบัน {current_price}".format(exchange=i['exchange'],coin=i['coin'],set_price=str(set_price),current_price=str(current_price))
                LineNotify(msg,i['token'])
        elif current_price > set_price and i['typenotify'] == 4 and i['status']:
            i['status'] = 0
            cmd = "UPDATE notify SET status='{status}' WHERE id={id}".format(status=i['status'],id=i['id'])
            res = SQL.RUN(cmd)
       



while True:
    time.sleep(1)
    GetPriceALL()

