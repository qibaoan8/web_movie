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
from config import RESOURCE_PATH

reload(sys)
sys.setdefaultencoding( "utf-8" )

def find_file(find_dir, end_key_work, web_dir="", filter_word="QR-1024"):
    """

    :param find_dir:
    :param end_key_work:
    :param web_dir:
    :param filter_word:
    :return:
    """

    ret_file = []
    file_list = os.listdir(os.path.join(RESOURCE_PATH, find_dir))

    for i in range(0, len(file_list)):
        web_path = os.path.join(web_dir, find_dir, file_list[i])
        if web_path[-len(end_key_work):].lower() == end_key_work.lower():
            if (filter_word == "" or
                    (filter_word != "" and file_list[i].lower().find(filter_word.lower()) == -1)):
                ret_file.append(web_path.decode('utf-8'))
    ret_file.sort()
    return ret_file



