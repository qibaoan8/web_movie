#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: update_db.py
Date: 2018-12-01 18:08
Author: wang.gaofei@alibaba-inc.com 
"""

import os
from models import Movies
from exts import db
from config import RESOURCE_PATH
from base.find_file import find_file
from str_coding import str_coding

def inset_db_from_local(movie_name, detail_path, photo_path):
    """
    将本地的电影摘要，插入到数据库内
    :param movie_name:
    :param detail_path:
    :param photo_path:
    :return:
    """

    movie = Movies.query.filter(Movies.detail_path == detail_path).first()
    if movie:
        if movie.name == movie_name and movie.photo_path == photo_path:
            return False
        else:
            movie.name = movie_name
            movie.photo_path = photo_path
            db.session.commit()
            return True
    else:
        movie = Movies(name=movie_name, detail_path=detail_path, photo_path=photo_path)
        db.session.add(movie)
        db.session.commit()
        return True


def scan_local_path():
    # 扫描本地所有的文件夹，把电影名称和路径都加载进去

    # 获取已经扫描过的列表
    scaned_path_list = []
    scaned_path_table = Movies.query.filter().all()
    for movie in scaned_path_table:
        scaned_path_list.append(movie.detail_path)

    path_list = os.listdir(RESOURCE_PATH)
    for path in path_list:
        if path in scaned_path_list:
            continue
        all_path = os.path.join(RESOURCE_PATH, path)

        if os.path.isdir(all_path):
            detail_path = path
            photo_list = find_file(os.path.join(RESOURCE_PATH, path), ".jpg")
            movie_list = find_file(os.path.join(RESOURCE_PATH, path), ".mp4")
            try:
                # 这个是给首页展示图片的url里面的文件路径 就是ddd/0000/filename.jpg filename.jpg那一部分，可以带目录，但要用/
                photo_path = photo_list[0].replace('\\','/')
            except:
                photo_path = ""

            try:
                movie_list.sort(reverse=True)
                movie_name = os.path.basename(movie_list[0])
                movie_name = str_coding(movie_name)
            except Exception as e:
                movie_name = u"未找到影片名称"
            inset_db_from_local(movie_name,detail_path,photo_path)
    return ""

