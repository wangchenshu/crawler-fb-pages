#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import requests
import pandas as pd 
from dateutil.parser import parse

import config

#在Facebook Graph API Exploer取得token
token = config.token
fanpage_id = config.fanpage_id
fanpage_name = config.fanpage_name

what_page_id = config.filter_page_id
if len(sys.argv) > 1:
    what_page_id = sys.argv[1]

    #在Facebook Graph API Exploer取得粉絲專頁的id與名稱，並將其包成字典dic
    fanpage = {fanpage_id : fanpage_name} 

    #建立一個空的list
    information_list = []

    out_file = 'who-likes-{0}.csv'.format(what_page_id)

    res = requests.get('https://graph.facebook.com/v2.9/{}/likes?summary=true&access_token={}'.format(what_page_id, token))

    #API最多一次呼叫100筆資料，因此使用while迴圈去翻頁取得所有的資料
    i = 0
    while 'paging' in res.json(): 
        for information in res.json()['data']:
            if 'id' in information:
                what_page = '"http://www.facebook.com/{0}"'.format(what_page_id)
                fb_user_link = '"http://www.facebook.com/{0}"'.format(information['id'])
                fb_user_name = '"%s"' % (information['name'])
                print fb_user_name
                information_list.append([i+1, what_page, fb_user_link, fb_user_name])
                i += 1

        if 'next' in res.json()['paging']:
            res = requests.get(res.json()['paging']['next'])
        else:
            break

    #最後將list轉換成dataframe，並輸出成csv檔
    information_df = pd.DataFrame(information_list, columns=['serial', 'fans_page', 'user_link', 'user_name'])
    information_df.to_csv(out_file, index=False, sep=',', encoding='utf-8', quoting=csv.QUOTE_NONE)
else:
    print 'Usage: python {0} <page-id>'.format(sys.argv[0])