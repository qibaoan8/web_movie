#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: zip.py
Date: 2018-12-14 11:24
Author: wang.gaofei@alibaba-inc.com 
"""
import zipfile, os, sys
reload(sys)
sys.setdefaultencoding('utf8')


def unzip_file(file_name, filter_words=['.mht','.url','QR-1024','htm']):
    """
    通过文件名的绝对路径进行解压，然后删除源文件。
    :param file_name:
    :return:
    """

    # file_name = "/Users/wang.gaofei/d/ddd/49084452.zip"
    dir_name = os.path.dirname(file_name)

    zip_file = zipfile.ZipFile(file_name, 'r')
    for file in zip_file.namelist():
        # zip_file.extract(file,dir_name)
        # continue

        # 修改文件编码
        try:
            _zip_file_name = file.decode('gbk')
        except:
            _zip_file_name = file

        # 创建目录
        if _zip_file_name[-1:] == "/":
            _dir_name = os.path.join(dir_name,_zip_file_name)
            if not os.path.exists(_dir_name):
                os.mkdir(_dir_name)
        else:
            in_key_word = False
            # 包含关键字的文件都不解压。
            for word in filter_words:
                if _zip_file_name.find(word) != -1:
                    in_key_word = True
                    break
            if in_key_word:
                continue
            # 解压文件
            _zip_file_name = os.path.join(dir_name,_zip_file_name)
            _dir_name = os.path.dirname(_zip_file_name)
            if not os.path.exists(_dir_name) and dir_name != "":
                os.mkdir(_dir_name)
            print _zip_file_name
            file_data = zip_file.read(file)
            fo = open(_zip_file_name, "wb")
            fo.write(file_data)
            fo.close()
    zip_file.close()
    os.remove(file_name)

if __name__ == '__main__':
    from convert_video import find_convert
    path = "J:\ddd\web_scan\\29821482.zip"
    unzip_file(path)
    find_convert(path[:-4])
    exit()
    from config import RESOURCE_PATH
    for name in  os.listdir(RESOURCE_PATH):
        if name.find('.zip') != -1:
            print os.path.join(RESOURCE_PATH,name)
            unzip_file(os.path.join(RESOURCE_PATH,name))



