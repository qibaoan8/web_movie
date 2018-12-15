#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
#

"""
File: str_coding.py
Date: 2018-12-15 19:39
Author: wang.gaofei@alibaba-inc.com
"""

import chardet

def str_coding(text):
    """
    目标是将任意一种字符集都能解码成人能看懂的字符集
    :param text:
    :return:
    """
    encoding = ""
    try:
        encoding = chardet.detect(text).get('encoding')
        if encoding == "ISO-8859-1":
            text = text.decode('gbk').encode('utf-8')
        else:
            text = text.decode(encoding)
    except Exception as e:
        if encoding == 'GB2312':
            text = text.decode('gb18030')
        else:
            text = text.decode('utf-8')
    return text
