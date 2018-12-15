#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: cat_photo.py
Date: 2018-12-08 12:08
Author: wang.gaofei@alibaba-inc.com 
"""
import requests
import json, time

def yun_da_ma(photo_2):

    data = {
        'username': 'qibaoan8',
        'password': 'nizhidao8',
        'codetype': '1005',
        'appid': '1',
        'appkey': '22cc5376925e9387a23cf797cb9ba745',
        'timeout': '60',
        'version': 'YAPI/WEB v1.0.0',
        'showimage': '1',
    }

    files = {'file':('yzm111.png', photo_2, 'image/jpeg', {'Expires': '0'})}

    # 发送上述post请求，也就是简单的
    url = 'http://api.yundama.net:5678/api.php?method=upload'
    res = requests.post(url,data, files=files)
    print res.content
    res_json = json.loads(res.content)
    text = res_json.get('text')
    if text == '':
        url = "http://api.yundama.net:5678/api.php?method=result&cid=%s" % res_json.get('cid')
        for i in range(10):
            time.sleep(2)
            res = requests.get(url)
            res_json = json.loads(res.content)
            if res_json.get('text') != '':
                text = res_json.get('text')
                break
    return text

if __name__ == '__main__':
    print yun_da_ma('verify_photo.png')

    verify_url = 'http://dufile.com/yzm.php'
    res = requests.get(verify_url)
    verify_text = yun_da_ma(res.content)
    print verify_text