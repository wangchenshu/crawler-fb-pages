#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pandas as pd 
from dateutil.parser import parse

import config

#在Facebook Graph API Exploer取得token以及粉絲專頁的ID
token = config.token
fanpage_id = config.fanpage_id
fanpage_name = config.fanpage_name
filter_page_id = config.filter_page_id

#建立一個空的list
information_list = []

out_file = 'all-likes.csv'

#目標頁面
res = requests.get('https://graph.facebook.com/v2.9/{}/posts?limit=100&access_token={}'.format(fanpage_id, token))
page = 1  

#API最多一次呼叫100筆資料，因此使用while迴圈去翻頁取得所有的文章
while 'paging' in res.json(): 
    for index, information in enumerate(res.json()['data']):
        print('正在爬取第{}頁，第{}篇文章'.format(page, index + 1))
        
        #判斷是否為發文，是則開始蒐集按讚ID
        if 'message' in information:
            res_post = requests.get('https://graph.facebook.com/v2.9/{}/likes?limit=1000&access_token={}'.format(information['id'], token))
            
            #判斷按讚人數是否超過1000人，若超過則需要翻頁擷取；當沒有人按讚時，按讚人名與ID皆為NO
            try:
                if 'next' not in res_post.json()['paging']:
                    for likes in res_post.json()['data']:
                        information_list.append([information['id'], information['message'], parse(information['created_time']).date(), likes['id'], likes['name']])                
                elif 'next' in res_post.json()['paging']:
                    while 'paging' in res_post.json():
                        for likes in res_post.json()['data']:
                            information_list.append([information['id'], information['message'], parse(information['created_time']).date(), likes['id'], likes['name']])
                        if 'next' in res_post.json()['paging']:
                            res_post = requests.get(res_post.json()['paging']['next'])
                        else:
                            break
            except:
                information_list.append([information['id'], information['message'], parse(information['created_time']).date(), "NO", "NO"])

    if 'next' in res.json()['paging']:                
        res = requests.get(res.json()['paging']['next'])
        page += 1
    else:
        break

user_list = []

for i in information_list:
    if i[0] == filter_page_id:
        user_id = i[3]
        user_name = i[4]
        user_page = 'https://www.facebook.com/' + user_id
        user_list.append([user_id, user_name, user_page])

print('爬取結束!')

#最後將list轉換成dataframe，並輸出成csv檔
information_df = pd.DataFrame(user_list, columns=['fans_id', 'user_name', 'user_link'])
information_df.to_csv(out_file, index=False, sep=',', encoding='utf-8')