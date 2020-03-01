#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import socket
import requests
import telegram
from time import sleep
from random import randrange
from datetime import datetime

class TGbot:
    def __init__(self):
        '''telegram消息机器人'''
        self.news={'data':[],'count':0}

    def get_news(self,headers_in,type=0):
        if type==0:
            ip=socket.gethostbyname(socket.gethostname())
            cts_time1=datetime.now().timestamp()-randrange(100,500)
            cts_time2=datetime.now().timestamp()
            #更新headers
            req_headers=headers_in.copy()
            req_headers['cookie']=req_headers['cookie'].format(ip=ip,time1=cts_time1,time2=cts_time2,time1_1=int(cts_time1*1000),time2_1=int(cts_time2*1000))
            last_id=req_headers['last_id']
            del req_headers['last_id']
            #更新请求参数
            req_params={'zhibo_id': 152,'id': '','tag_id': 0,'page': 1,'page_size': 40,'type': 0}
            req_params['callback']='t'+str(cts_time2)[:8]

            #获取原始的接口数据
            news_raw=json.loads(requests.get("https://zhibo.sina.com.cn/api/zhibo/feed",params=req_params,headers=req_headers).text[24:-15])
            if news_raw['status']['code'] != 0:
                self.news={'data':[(last_id,str(datetime.now())[:19],'异常通知','获取消息异常，请管理员检查服务是否可用！')],'count':1,'last_id':last_id}
            elif len(news_raw['data']['feed']['list'])>0:
                news_list=[(news['id'],news['create_time'],','.join([tag['name'] for tag in news['tag']]),news['rich_text']) for news in news_raw['data']['feed']['list'][::-1] if news['id']>last_id]
                last_id=max([x[0] for x in news_list])
                self.news={'data':news_list,'count':len(news_list),'last_id':last_id}
            else:
                pass

    def push_news(self):
        '''开始推送消息'''
        if self.news['count']>0:
            bot = telegram.Bot(token='123456789:AAHgcxsU51K9CHaGg-E5BsNmasVfgvunXB4')
            for msg in self.news['data']:
                bot.send_message(chat_id='@dailynewsyc',
                    text='<b>消息: {id}\n标签: {tag}\n时间：{time}</b>\n\n{text}.'.format(id=msg[0],time=msg[1],tag=msg[2],text=msg[3]),
                    parse_mode=telegram.ParseMode.HTML,timeout=60)
                sleep(randrange(1,5))
            if self.news['data'][-1][2] != '异常通知':
                bot.send_message(chat_id='@dailynewsyc',text='本次共发送消息{}条，更新时间为{}'.format(self.news['count'],self.news['data'][-1][1]),timeout=60)


if __name__ == '__main__':
    project_path=os.path.join(os.path.expanduser('~'),'tgbot')
    headers_file=os.path.join(project_path,'src/headers.json')

    with open(headers_file) as file:
        headers=json.loads(file.read())

    tgbot=TGbot()
    tgbot.get_news(headers_in=headers)
    tgbot.push_news()

    headers['last_id']=tgbot.news['last_id']
    with open(headers_file,'wt',encoding='utf-8') as file:
        file.write(json.dumps(headers,indent=4))
