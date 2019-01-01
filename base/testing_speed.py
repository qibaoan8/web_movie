#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: cesu.py
Date: 2019-01-01 17:40
Author: wang.gaofei@alibaba-inc.com 
"""
import time
import threading
import urllib2


class Download(threading.Thread):
    def __init__(self, url, headers):
        threading.Thread.__init__(self)
        self.url = url
        self.headers = headers
        self.thread_num = 1
        self.interval = 1
        self.thread_stop = False
        self.datasize = 0
        self.start_time = 0
        self.end_time = 0

    def do_download(self, url, headers):
        buffer_size = 1024
        try:
            req = urllib2.Request(url, headers=headers)
            uf = urllib2.urlopen(req, timeout=4)
            self.start_time = time.time()
            while True:
                data = uf.read(buffer_size)
                if not data or self.thread_stop: break
                self.datasize += buffer_size
        except Exception as e:
            pass

    def run(self):
        self.do_download(self.url, self.headers)

    def terminate(self):
        self.thread_stop = True

def testing_speed(url, headers={}, timeout=5):
    download = Download(url, headers)
    download.daemon = True
    download.start()

    time.sleep(timeout)

    download.end_time = time.time()
    download.terminate()
    delta = download.end_time - download.start_time
    # speed B/s
    speed = int(download.datasize / delta)

    return speed

if __name__ == '__main__':
    urls = [
        "http://v961.sufile.net:3657/down/5c81379728b20667.zip?key=z0%2F4VFaz0ANRzcXbn%2Bl%2BW0zDjD3%2Fam0BzoXbEBuTD1IrN3lHqqsYo6vQMNlXHnlq400nol5L%2B%2BCUZnIdzrXLcYSoM2i6969nteuOyG%2FPohAfVgTrSOUGopiFtmhkfO1ggfJNI6yWZlx8nWx1G%2Fmwrk%2BVpdLuAig",
        "http://v962.sufile.net:3657/down/5c81379728b20667.zip?key=yR2uAVbh0V9RzcXbn%2Bl%2BW0zDjD3%2Fam0BzoXbEBuTD1IrN3lHqqsYo6vQMNlXHnlq400nol5L%2B%2BCUZnIdzrXLcYSoM2i6969nteuOyG%2FPohAfVgTrSOUGopiFtmhkfO1ggfJNI6yWZlx8nWx1G%2Fmwrk%2BVptXqAig",
        "http://s96.sufile.net:3642/down/5c81379728b20667.zip?key=yR2uAVbh0V9RzcXbn%2Bl%2BW0zDjD3%2Fam0BzoXbEBuTD1IrN3lHqqsYo6vQMNlXHnlq400nol5L%2B%2BCUZnIdzrXLcYSoM2i6969nteuOyG%2FPohAfVgTrSOUGopiFtmhkfO1ggfJNI6yWZlx8nWx1G%2Fmwrk%2BVptXqAig",
    ]
    headers = {
        "Cookie":"C_user_id=2019010117524476960"
    }

    for url in urls:
        print url
        print testing_speed(url,headers)


