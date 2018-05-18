# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:49:07 2018

@author: Liu-pc
"""
import re
import pandas as pd
import json
import urllib2
train_list_url = 'https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0'

data = urllib2.urlopen('https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0')
data = data.read()     
data1 =data[16:]      
data1 = json.loads(data1) 
data2 =pd.DataFrame(data1)

a = pd.DataFrame()     
for i in data2.axes[0]:
    for j in data2.axes[1]:
        b = pd.DataFrame(data2.loc[i,j])
        b['class'] = i
        a = pd.concat([a, b])
a = a.drop_duplicates()      

on_station = map(lambda x: x.split('(')[1].split('-')[0], a['station_train_code'])
off_station = map(lambda x: x.split('(')[1].split('-')[1].split(')')[0], a['station_train_code'])
####得到所有上下车的名称
a['on'] = on_station
a['off'] = off_station
a.index = range(len(a))


#####站点对应
url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9053'
r = urllib2.urlopen(url)
r = r.read()

result = r.replace('var station_names =\'', '').replace('\'', '').replace(';', '')
station = result.split('@')
station = station[1:]

station_chinese = map(lambda x: x.split('|')[1], station)  #中文站点
station_code = map(lambda x: x.split('|')[2], station)   #代号
 
station_name= {}        #生成字典
for i in range(len(station_code)):
    station_name[station_chinese[i]] = station_code[i]



##############

import urllib2
import ssl
import json

def getresult(date, on, off):
    #得到url 返回的数据， 带有时间
    url =  'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT'%(date,on,off)
    html = urllib2.urlopen(url).read()
    dict = json.loads(html)
    result = dict['data']['result']
    return result


def get_time(result):
    #从url返回的数据中，提取转换为数据框
    on_time = []
    off_time = []
    checi = []
    train_no = []
    data = pd.DataFrame()
    for i in range(len(result)):
        on_time.append( result[i].split('|')[8])
        off_time.append( result[i].split('|')[9])
        checi.append(result[i].split('|')[3])
        train_no.append(result[i].split('|')[2])
    data['on_time'] = on_time
    data['off_time'] = off_time
    data['checi'] = checi
    data['train_no'] = train_no
    return data
        
on_station= map(lambda x: x.encode('utf-8') , on_station) 
off_station = map(lambda x: x.encode('utf-8') , off_station)

def get_onelink(date, on_station, off_station):
    data = pd.DataFrame()
    link = getresult(date, station_name[on_station], station_name[off_station])
    data = get_time(link)
    data['on_station'] = on_station
    data['off_station'] = off_station
    return data

data = pd.DataFrame()
for i in range(len(a)):
    if (on_station[i] in  station_name.keys()) and (off_station[i] in  station_name.keys()) :
        data = pd.concat([data,get_onelink('2018-05-22', on_station[i], off_station[i])])
        print i
    else :
        continue
#抓取所有搜索结果界面数据
##########################################    

#抓取中间站点数据
#使用a， 以及on_station， off_station,date
def get_all_pathlink(train_no, from_, to_, date):
    url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date=%s'%(train_no, station_name[from_], station_name[to_], date)
    #包含train_no,from ,to ,date
    ree = urllib2.urlopen(url) 
    ree = ree.read()
    ree= json.loads(ree) 
    link_  = ree['data']['data']
    arrive_time = []
    leave_time = []
    station_no = []
    stationname = []
    all_link = pd.DataFrame()
    if link_ != []:
        for i in link_:
            arrive_time.append(i['arrive_time'])
            leave_time.append(i['start_time'])
            station_no.append(i['station_no'])
            stationname.append(i['station_name'])
        
        all_link['arrive_time'] = arrive_time
        all_link['start_time'] = leave_time
        all_link['station_name'] = stationname
        all_link['station_no'] = station_no
        all_link['first_station'] =  from_
        all_link['last_station'] = to_
        all_link['train_code'] = link_[0]['station_train_code']
    return all_link


all_link =  pd.DataFrame()
train_no = list(a['train_no'])
for i in range(len(a))[4710:]:
    if (on_station[i] in  station_name.keys()) and (off_station[i] in  station_name.keys())  :
        all_link = pd.concat([all_link,get_all_pathlink(train_no[i], on_station[i], off_station[i], '2018-05-25' )])
        print i

###得到所有中间站点,