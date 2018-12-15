#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: http_base.py
Date: 2018-12-02 23:55
Author: wang.gaofei@alibaba-inc.com 
"""

import urllib

def get_url_host(url):
    protocol, s1 = urllib.splittype(url)
    host, s2 = urllib.splithost(s1)
    host, port = urllib.splitport(host)
    return host