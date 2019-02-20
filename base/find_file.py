#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: find_file.py
Date: 2018-12-01 15:03
Author: wang.gaofei@alibaba-inc.com 
"""

import os,sys
from str_coding import str_coding

reload(sys)
sys.setdefaultencoding( "utf-8" )

def find_file_keys(find_path, end_key_works, filter_word=["QR-1024"]):
    ret_file = []
    for key in end_key_works:
        ret_file += find_file(find_path, key, filter_word)
    return ret_file

def find_file(find_path, end_key_work, filter_word=["QR-1024"]):
    """

    :param find_dir:
    :param end_key_work:
    :param filter_word:
    :return:
    """


    def _find_dir_file(find_path, list, end_keyword):
        """
        深度查找目录内指定格式的所有文件
        :param path:
        :param list:
        :param end_keyword:
        :return:
        """
        def _is_include(text, key_list):
            """
            用于匹配绝对路径内是否包含传入的所有关键字
            :param text:
            :param key_list:
            :return:
            """
            for key in key_list:
                if key in text:
                    return True
            return False

        file_list = os.listdir(find_path)

        for filename in file_list:
            file_path = os.path.join(find_path,filename)
            if os.path.isdir(file_path):
                _find_dir_file(file_path, list, end_keyword)
            else:
                if file_path.endswith(end_keyword) and not _is_include(file_path, filter_word):
                    list.append(file_path)

    find_file_list = []
    _find_dir_file(find_path,find_file_list,end_key_work)

    ret_file_list = []
    master_path_len = len(find_path) + 1 # 加1 是因为两个路径中间那个斜线。 os.join有一个识别，如果有那个斜线合并就有问题
    for file_name in find_file_list:
        file_name = file_name[master_path_len:]
        file_name = str_coding(file_name)
        ret_file_list.append(file_name)

    try:
        ret_file_list.sort()
    except:
        pass
    return ret_file_list

def find_file_web(find_path, end_key_work, web_dir="", filter_word=["QR-1024"]):
    from config import RESOURCE_PATH

    master_path = os.path.join(RESOURCE_PATH, find_path)
    master_path_len = len(master_path) + 1

    find_file_list = find_file(master_path, end_key_work, filter_word)
    ret_file_list = []
    print find_file_list
    for file_path in find_file_list:
        web_path = os.path.join(web_dir, file_path[master_path_len:]).replace('\\', '/')
        ret_file_list.append(web_path)

    return ret_file_list


if __name__ == '__main__':
    for i in find_file_web('62467175','.jpg','http://movie.gaofei.com/ddd/624/'):
        print i


