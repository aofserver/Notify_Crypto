import os
import ast
import re
import time
import random
import datetime
import hashlib
from typing import List

import requests
from Database import SQL
from pydantic import BaseModel
from fastapi import File, Form, UploadFile, APIRouter, Request



router = APIRouter(
    prefix="/notify",
    tags=["Notify"],
    responses={404: {"message": "Not found"}}
)

def LineNotify(msg,token):
  url = 'https://notify-api.line.me/api/notify'
  headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer ' + token}
  r = requests.post(url, headers=headers, data = {'message':msg})
  r = r.json()
  return r



def ValidateUser(id,token):
    cmd = "SELECT tokenlinenoti FROM userinfo WHERE id={};".format(id)
    res = SQL.Query(cmd)
    if len(res) == 0:
        return False
    return res[0]['tokenlinenoti'] == token



class otplinenotify(BaseModel):
    msg: str
@router.post("/otplinenotify") 
async def OTPLineNotify(otplinenotify:otplinenotify,request: Request):
    data = otplinenotify.dict()
    tokenlinenoti = request.headers.get('Authorization').split(" ")[-1]
    return LineNotify(data['msg'],tokenlinenoti)


@router.get("/getnotify") 
async def GetNotify(request: Request):
    userid = request.headers.get('userid')
    cmd = "SELECT notify.id,exchange.name,notify.coin,typenotify.detail,notify.price,notify.cntnotify  FROM notify INNER JOIN exchange ON notify.exchange_id=exchange.id JOIN typenotify ON notify.typenotify=typenotify.id WHERE userinfo_id={};".format(userid)
    notify = SQL.Query(cmd)
    return notify


class registernotify(BaseModel):
    name: str
@router.post("/registernotify")
async def RegisterNotify(registernotify:registernotify,request: Request):
    data = registernotify.dict()
    tokenlinenoti = request.headers.get('Authorization').split(" ")[-1]

    cmd = "SELECT * FROM userinfo WHERE tokenlinenoti='{}';".format(tokenlinenoti)
    if len(SQL.Query(cmd)) == 0:
        id = int(time.time())
        cmd = "INSERT INTO userinfo (id, name, tokenlinenoti) VALUES ( {id},'{name}','{tokenlinenoti}');".format(id=id,name=data['name'],tokenlinenoti=tokenlinenoti)
        res = SQL.RUN(cmd)
    cmd = "SELECT * FROM userinfo WHERE tokenlinenoti='{}';".format(tokenlinenoti)
    return SQL.Query(cmd)


class setnotify(BaseModel):
    exchange: str
    typecoin: str
    typenotify: str
    price: str
@router.post("/setnotify")
async def SetNotify(setnotify:setnotify,request: Request):
    data = setnotify.dict()
    tokenlinenoti = request.headers.get('Authorization').split(" ")[-1]
    userid = request.headers.get('userid')
    if ValidateUser(userid,tokenlinenoti):
        cmd = "INSERT INTO notify (exchange_id, coin, typenotify, price, userinfo_id, status, cntnotify) VALUES ({exchange},'{coin}',{typenotify},{price},{userinfo_id},0,0);".format(exchange=data['exchange'],coin=data['typecoin'],typenotify=data['typenotify'],price=data['price'],userinfo_id=userid)
        res = SQL.RUN(cmd)
        reply = { 'status':res }
        return reply
    return { 'status':False }


class deletenotify(BaseModel):
    id: int
@router.post("/deletenotify")
async def DeleteNotify(deletenotify:deletenotify,request: Request):
    data = deletenotify.dict()
    tokenlinenoti = request.headers.get('Authorization').split(" ")[-1]
    userid = request.headers.get('userid')
    if ValidateUser(userid,tokenlinenoti):
        res = SQL.RUN("DELETE FROM notify WHERE id={};".format(data['id']))
        reply = { 'status':res }
        return reply
    return { 'status':False }


@router.get("/exchange") 
async def GetExchange():
    listexchange = SQL.Query("SELECT * FROM exchange;")
    return listexchange


@router.get("/typecoin") 
async def GetTypecoin(exchange: str):
    listtypecoin = SQL.Query("SELECT * FROM typecoin WHERE exchange={};".format(exchange))
    return listtypecoin


@router.get("/typenotify")
async def GetExchange():
    listtypenotify = SQL.Query("SELECT * FROM typenotify;")
    return listtypenotify