# !/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
#

"""
File: dufile.py
Date: 2018-12-02 23:50
Author: wang.gaofei@alibaba-inc.com
"""
import os, requests, cookielib, time
from http_base import get_url_host
from config import RESOURCE_PATH
from download_movie import Down_Load
from download_movie2 import download_sync
from config import DUFILE_USERNAME, DUFILE_PASSWORD, is_proxy, local_proxy
from cat_photo import yun_da_ma
from unzip_file import unzip_file
from log_config import init_log
from testing_speed import testing_speed
from convert_video import find_convert

file_path = os.path.abspath(os.path.dirname(__file__))
log = init_log("dufile_logic", "../logs/")


class DuFile():
    def __init__(self):
        self.url = "http://dufile.com/member/"
        self.host = get_url_host(self.url)
        self.dir_name_id = []
        self.http_timeout = 10 # 秒
        self.proxies = {'http': local_proxy, 'https': local_proxy}

        # 初始化cookie环境
        self.cookie_path = "cookie.txt"
        # 将LWPCookieJar类型的cookie 赋值给 RequestsCookiesJar类型的cookie；也能使用，绝了。
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(self.cookie_path)
        if os.path.exists(self.cookie_path):
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)

    def request_http(self, url, data=None, headers=None):
        """
        类似一个请求工具，自动添加重试，或者自动添加代理
        :param url:
        :param data:
        :return: response
        """
        def _request_http(http_session,url,data,proxies,timeout,headers):
            if data:
                response = http_session.post(url, data, proxies=proxies, timeout=timeout,headers=headers)
            else:
                response = http_session.get(url, proxies=proxies, timeout=timeout,headers=headers)
            return response

        try:
            proxies = {}
            response = _request_http(self.session, url, data, proxies, self.http_timeout,headers)
        except:
            proxies = self.proxies
            response = _request_http(self.session, url, data, proxies, self.http_timeout,headers)

        return response

    def check_login(self, key=DUFILE_USERNAME):
        url = 'http://dufile.com/member/'
        res = self.request_http(url)
        if res.content.find(key) != -1:
            return True
        return False

    def login(self, username, passpord):
        index_url = 'http://dufile.com/'
        self.request_http(index_url)

        verify_url = 'http://dufile.com/yzm.php'
        res = self.request_http(verify_url)
        verify_text = yun_da_ma(res.content)
        log.info('正在登陆-验证码识别:%s' % verify_text)
        login_url = 'http://dufile.com/post.php'
        data = {
            'type': 'login',
            'nick': DUFILE_USERNAME,
            'pwd': DUFILE_PASSWORD,
            'yzm': verify_text
        }
        headers = {
            'Referer': 'http://dufile.com/'
        }
        res = self.request_http(login_url, data, headers=headers)
        log.info('登陆请求发送结果:%s' % res.content)

        return self.check_login()

    def save_cookie(self):
        self.session.cookies.save(ignore_discard=True, ignore_expires=True)
        return

    def get_file_list(self):
        html_body = self.request_http(self.url).content
        file_list = []

        file_id = 0  # 初始化一个默认的值
        for line in html_body.split("\n"):
            # 先获取file id ，存起来
            if line.find('type="checkbox" value="') != -1:
                file_id = line.split('value="')[1].split('"')[0]
                log.info('find file id is: {}'.format(file_id))
                continue

            if line.find("name file-title f14") != -1:
                # 获取文件列表页的名称
                file_name = line.split('title="')[1].split('"')[0]
                file_page_url = line.split('href="')[1].split('"')[0]
                file_page_url = "http://dufile.com/vip/" + os.path.basename(file_page_url)
                log.info('find file name is: {}'.format(file_name))
                _html_body = self.request_http(file_page_url).content
                urls = []
                log.info('get file url info.')
                for line in _html_body.split("\n"):

                    # 获取文件的url
                    if line.find('id="vipdown"') != -1:
                        for i in line.split('href="'):
                            if i.find("http://") != -1:
                                urls.append(i.split('"')[0])
                file = {
                    "file_name": file_name,
                    "urls": urls,
                    "file_id": file_id
                }
                log.info('file detail is: {}'.format(file))
                file_list.append(file)
                break

        return file_list

    def get_dir_id_list(self):
        import re
        dir_list = []
        html_body = self.request_http(self.url).content
        for line in html_body.split("\n"):
            if line.find('var folder=') != -1:
                for dir in line.split('option value="'):
                    if dir.find('var folder=') != -1:
                        continue
                    dir_id = dir.split('"')[0]
                    dir_name = re.split("[<>]", dir)[1]

                    dir_object = {
                        "dir_name": dir_name,
                        "dir_id": dir_id
                    }
                    dir_list.append(dir_object)

                break
        return dir_list

    def mv_dir(self, file_id, src_dir_id, dst_dir_id):
        # dirid: 0   源目录 id
        # muluid: 4  目标目录id

        # --data 'muluid=1&dirid=3&fileid=2516154&type=yid_file'
        url = "http://dufile.com/member/file_post.php"
        post_data = {
            "dirid": src_dir_id,
            "muluid": dst_dir_id,
            "fileid": file_id,
            "type": "yid_file"
        }
        # Referer: http://dufile.com/member/?folderid=3&order=sizedown
        headers = {
            "Referer": "http://dufile.com/member/?folderid=%s&order=sizedown" % src_dir_id
        }
        res = self.request_http(url, data=post_data, headers=headers)
        return res.content

def start():
    down_local_path = RESOURCE_PATH
    df = DuFile()

    while True:
        log.info('开始判断登陆状态')
        while not df.check_login():
            log.info('正在登陆...')
            status = df.login(DUFILE_USERNAME, DUFILE_PASSWORD)
            log.info('登陆状态：%s' % status)

        log.info('登陆成功')
        df.save_cookie()

        file_list = df.get_file_list()
        df.save_cookie()
        log.info('获取页面上的文件列表，共计%s个' % len(file_list))

        if len(file_list) == 0:
            time.sleep(600)
            continue

        file_object = file_list[0]
        file_name = file_object['file_name']
        file_id = file_object['file_id']
        urls = file_object['urls']
        log.info('开始测试url的下载速度，一个5秒')
        speed_json = {}
        headers = {
            'Cookie': "C_user_id=%s" %
                      requests.utils.dict_from_cookiejar(df.session.cookies)['C_user_id']
        }
        for url in urls:
            speed = testing_speed(url, headers=headers)
            speed_json[str(speed)] = url
            log.info('测速：%s B/s , url:%s' % (speed, url))

        speeds = map(int, speed_json.keys())
        max_speed = max(speeds)
        max_url = speed_json.get(str(max_speed))
        log.info('最大速度：%s B/s , url:%s' % (max_speed, max_url))
        url = max_url

        log.info('文件：%s, 下载地址: %s' % (file_name, url))

        # 旧版下载方法
        # down = Down_Load(5, df.session.cookies)
        # file_length = down.get_file_length(url)
        # log.info('文件大小为:%s' % file_length)
        # down.download(url, file_name, down_local_path, file_length / 2 + 1)

        # 新版下载方法
        # C_user_id=2019011921022040087
        cookies = {
            'C_user_id':requests.utils.dict_from_cookiejar(df.session.cookies)['C_user_id']
        }

        download_status = download_sync({
            'url':url,
            'path':os.path.join(down_local_path,file_name),
            'cookies': cookies
        })

        if download_status:
            log.info('下载完毕，正在将文件移动到已下载目录')
            df.mv_dir(file_id, 0, 1)  # 1 已下载
            log.info('目录移动完毕，正在解压文件')
            unzip_file(os.path.join(down_local_path, file_name))
            log.info('文件解压完毕,开始转换视频文件')
            find_convert(os.path.join(down_local_path, file_name)[:-4])
            log.info("视频文件转换完毕")
        else:
            log.info("下载超时，重新刷新再下载")


if __name__ == '__main__':
    start()
