#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: download_movie2.py
Date: 2019-01-13 14:47
Author: wang.gaofei@alibaba-inc.com 
"""

import time,os,traceback,sys
import threading
import urllib2,requests
from log_config import init_log
from contextlib import closing


file_path = os.path.abspath(os.path.dirname(__file__))
log = init_log("download", "../logs/")


class Download(threading.Thread):
    def __init__(self, url, filename, headers={}, cookies={}):
        threading.Thread.__init__(self)
        # 下载参数
        self.url = url
        self.filename = filename
        self.filename_tmp = filename + ".tmp"
        self.headers = headers
        self.cookies = cookies

        # 线程初始化参数
        self.thread_num = 1
        self.interval = 1

        # 文件下载属性
        self.buffer_size = 10240 # 10K
        self.file_size_all = 0
        self.file_size_finish = 0
        self.downlaod_speed = 0

        # 逻辑控制参数
        self.thread_stop = False
        self.finish = False   # 是否下载完成
        self.status = False   # 下载完成后的状态

    def run(self):
        self.do_download(self.url, self.filename, self.headers, self.cookies, )
        return

    def do_download(self, url, filename, headers, cookies):

        # 获取文件大小
        self.file_size_all = int(requests.head(url,headers=headers,cookies=cookies).
                                 headers['Content-Length'])

        # 和服务端建立连接，流数据方式获取
        res = requests.get(url,headers=headers,cookies=cookies,stream=True)

        start_time = time.time()
        write_buffer = ""

        # 打开建立的连接，逐渐获取数据
        with closing(res) as res_connect:
            log.info("download create connect %s" %url)
            # 打开文件，逐秒往里面写数据
            with open(self.filename_tmp, 'wb') as fd:
                log.info("download create local file %s" %filename)
                for buffer in res_connect.iter_content(self.buffer_size):
                    # 不足1秒的数据先写入buffer，减轻磁盘压力
                    write_buffer += buffer
                    self.file_size_finish += self.buffer_size

                    # 测试当前下载速度
                    time_diff = time.time() - start_time
                    if time_diff >= 1:
                        fd.write(write_buffer)
                        log.info("Download file: %s, filesize: %sMB/%sMB, speed: %s KB/s"
                                 %(filename,
                                   int(self.file_size_finish/1024/1024),
                                   int(self.file_size_all/1024/1024),
                                   int(len(write_buffer)/time_diff/1024))
                                   )
                        start_time = time.time()
                        write_buffer = ""

                # for 循环之后，如果buffer里面还有数据，追加一下。
                if write_buffer: fd.write(write_buffer)
                log.info("download finish, receive done.")
            # 下载数据流程正确
            self.status = True
            log.info("close download file finish.")
            # 更名为新名字
            os.rename(self.filename_tmp, self.filename)
            log.info("rename file name finish.")
        # 关闭了所有连接，下载结束
        self.finish = True
        return

    def terminate(self):
        self.thread_stop = True

def download_sync(down_object, timeout=3600):
    url = down_object['url']
    path = down_object['path']
    cookies = down_object['cookies']
    download = Download(url, path, cookies=cookies)
    download.daemon = True
    download.start()

    sleep_time = 0
    while not download.finish:
        time.sleep(3)
        sleep_time += 3
        if sleep_time > timeout:
            download.terminate()
            return False
    return True

if __name__ == '__main__':
    #
    # url="http://dl.2345.com/haozip/haozip_v5.9.8.10907.exe"
    # url="https://www.python.org/ftp/python/2.7.15/Python-2.7.15.tgz"
    # download = Download(url,"Python.exe")
    # download.daemon = True
    # download.start()
    #
    # while not download.finish:
    #     time.sleep(3)

    down = {
        'url':"http://dl.2345.com/haozip/haozip_v5.9.8.10907.exe",
        'path':"Python.exe"
    }

    download_sync(down)
