#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: curl_cookie.py
Date: 2018-12-01 21:58
Author: wang.gaofei@alibaba-inc.com 
"""


import cookielib
import requests
import os


class CurlCookie(object):
    """
    通过读取现有文件里面存储的cookie，去请求页面的数据，可以多线程并发处理，处理完毕后会把最新的cookie存入文件
    """

    def __init__(self, path):
        """
        根据文件的路径，初始化现有的cookie
        :param path:
        """
        self.path_cookie = os.path.dirname(os.path.abspath(__file__)) + "/cookies/" + path

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        }

        # 将LWPCookieJar类型的cookie 赋值给 RequestsCookiesJar类型的cookie；也能使用，绝了。
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(self.path_cookie)
        if os.path.exists(self.path_cookie):
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)


    def save(self):
        """
        将现在的cookie保存到硬盘上
        :return:
        """
        self.session.cookies.save(ignore_discard=True, ignore_expires=True)
        return True

if __name__ == "__main__":
    s = CurlCookie("n.alibaba-inc.com")
    data = s.session.get("https://n.alibaba-inc.com/api/ops/app/amap-petest/res/SERVER?_input_charset=utf-8&nodeGroup=amap-petest-host-et2&idc=&status=&unit=&isCategory=true&pageIndex=1&pageSize=10")
    print data.text
    print data.status_code
    print data.cookies
    s.save()
