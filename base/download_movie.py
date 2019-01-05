#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: download_movie.py
Date: 2018-12-01 20:28
Author: wang.gaofei@alibaba-inc.com 
"""
import urllib, os
import threading
import sys
import ctypes

reload(sys)

sys.setdefaultencoding('utf-8')

import requests
from curl_cookie import CurlCookie
from super_queue import Super_Queue
from log_config import init_log
from http_base import get_url_host

log = init_log("download","../logs/")

class Store_file():
    def __init__(self, file_path, file_size, file_block):
        self.file_path_finish = file_path
        self.file_path_tmp = file_path + ".tmp"
        self.file_path_cfg = file_path + ".cfg"
        self.file_size = file_size
        self.file_block = file_block
        self.file_data_fd = None
        self.file_cfg_fd = None

    def init_files(self):

        def init(file_path, file_size, block=None):
            # 填充文件的大小
            def write_null_body(file_path, file_size, block=None):
                file = open(file_path, "r+")
                file.truncate(file_size)
                if block:
                    file.seek(0,0)
                    for i in range(file_size):
                        file.write("0")
                file.close()
                return

            # 判断文件是否存在
            if not os.path.exists(file_path):
                fp = open(file_path, "w")
                fp.close()
                write_null_body(file_path, file_size, block)

            # 判断文件大小是否正确
            if os.path.getsize(file_path) != file_size:
                write_null_body(file_path, file_size, block)

        # (A+B-1)/B  是向上取整方法
        init(self.file_path_tmp, self.file_size)
        init(self.file_path_cfg, (self.file_size + self.file_block - 1) / self.file_block, "0")

        return

    def update_file(self, body, seek):
        """
        在文件的任意位置更新
        :param body: 数据内容
        :param seek: 位置到什么位置，单位为字节
        :return:
        """


        # 更新数据文件
        if not self.file_data_fd:
            self.file_data_fd = open(self.file_path_tmp, 'rb+')

        self.file_data_fd.seek(seek, 0)
        self.file_data_fd.write(body)
        self.file_data_fd.flush()

        # 更新配置文件
        if not self.file_cfg_fd:
            self.file_cfg_fd = open(self.file_path_cfg, 'r+')
        self.file_cfg_fd.seek(seek / self.file_block, 0)
        self.file_cfg_fd.write("1")
        self.file_cfg_fd.flush()
        return

    def read_file_config(self):
        file = open(self.file_path_cfg, "r")
        body = file.read()
        file.close()
        return body

    def finish_file(self):
        """
        删除配置文件，临时文件更名
        :return:
        """
        self.file_cfg_fd.close()
        self.file_data_fd.close()
        os.rename(self.file_path_tmp, self.file_path_finish)
        os.remove(self.file_path_cfg)
        return

class Down_Load():
    """
    一个下载器，通过多线程方式将文件下载到本地，支持断点续传；
    """

    def __init__(self, worker_num, cookies):
        self.worker_num = worker_num
        self.block_size = 1024 * 1024  # default 1M
        self.file_length = 0
        self.cookies = {
            'C_user_id':requests.utils.dict_from_cookiejar(cookies)['C_user_id']
        }

    def get_file_length(self,url):
        self.url = url
        if self.file_length == 0:
            # 获取url的host信息
            host = get_url_host(url)

            # 设置下载环境的cookie信息，获取文件大小
            self.socket = CurlCookie(host)
            data_length = int(self.socket.session.head(url,cookies=self.cookies).headers['Content-Length'])
            self.file_length = data_length

        return self.file_length

    def download(self, url, file_name, store_path, block_size):
        self.file_name = file_name
        self.store_path = store_path
        self.block_size = block_size

        data_length = self.get_file_length(url)
        block_number = (data_length + self.block_size - 1) / self.block_size

        log.info("get file size, %s size is %s M" % (file_name, data_length / 1024 / 1024))


        # 对大文件进行小段拆分，分段多线程下载
        block_down_list = []
        for number in range(block_number):
            block_down_object = {
                "start": number * self.block_size
            }
            if number == block_number - 1:
                block_down_object['len'] = data_length - number * self.block_size
            else:
                block_down_object['len'] = self.block_size
            block_down_list.append(block_down_object)
        log.info("down task plan, task number is %s, task block is %s K"
                                            %(block_number,self.block_size/1024))

        # 初始化文件存储对象
        self.file = Store_file(os.path.join(store_path, file_name), data_length, self.block_size)
        self.file.init_files()
        log.info("store file init finish.")

        # 创建多线程任务，开始下载
        sq = Super_Queue(self.worker_num)
        self.save_lock = threading.Lock()
        log.info("down threading init finish, worker number is %s" %self.worker_num)

        sq.start(self.down_block,block_down_list)
        self.file.finish_file()
        log.info("file %s download finish." %file_name)

        return

    def down_block(self, block_down_object):
        # vip961.sufile.net:3657
        # vip962.sufile.net:3657
        # s96.sufile.net:3642

        import random
        threading_id = random.randint(1,self.worker_num)

        headers = {
            "Range": "bytes=%s-%s" % (block_down_object['start'],
                                      block_down_object['start'] + block_down_object['len'])
        }
        log.info("threading id %s bagin download data, Rang is %s"%(threading_id, headers['Range']))

        # 获取块数据
        log.info("bagin get data")
        res = self.socket.session.get(self.url, headers=headers, cookies=self.cookies)
        log.info("over get data, size is %s" % len(res.content))
        # self.socket.save()  # 保存curl 库的cookie数据

        # print len(res.text)
        log.info("threading id %s in Rang %s download finish, writing to file"
                                                    %(threading_id, headers['Range']))

        # 通过锁机制，单线程写入文件
        if self.save_lock.acquire():

            # 这里踩了一个坑，原来用的res.text，耗时很久 需要19秒，各种日志才查出来这个问题；
            # res.text 是将get获取的byte类型数据自动编码，是str类型，res.content是原始的byte类型数据
            self.file.update_file(res.content, block_down_object['start'])

            self.save_lock.release()

        log.info("threading id %s in Rang %s write file finish."% (threading_id, headers['Range']))

        return



if __name__ == '__main__':
    log.info("start download.")

    # dufile 网站使用的还是垃圾的http1.0，range参数只支持从头到中间，从中间到末尾这两种类型。
    # 所以分线程，最多分两个。

    url = "http://a961.sufile.net:3657/down/5c81379728b20667.zip?key=mBj1UFHt1VBRzcXbn%2Bl%2BW0zDjD3%2Fam0BzoLSDQGYFVc8KHJEteBbrarHOeBYN2x26UEUsnJb%2BuOPbH4ux4PUbKvuX2uymqYJ2OjgpW%2BnoxYbU2%2FuJOYOopKFtmlhfONiifJEIq2RIxJpl3k0Uvyzr0mUp9XsSSBBKg"
    # url = "https://qd.myapp.com/myapp/qqteam/pcqq/QQ9.0.8.exe"
    cookie = {
        'C_user_id':'2019010511024220248'
    }

    down = Down_Load(5,cookie)
    file_length = down.get_file_length(url)
    down.download(url,"e717381c5b933a88.zip","",file_length/2+1)









