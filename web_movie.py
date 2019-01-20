#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
#

"""
File: web_movie.py
Date: 2018-12-01 15:03
Author: wang.gaofei@alibaba-inc.com
"""
from flask import Flask, render_template, request, redirect, url_for, session, g
import config,os
from base.find_file import find_file
from base.update_db import scan_local_path
from exts import db
from models import Movies
from sqlalchemy import or_
from config import RESOURCE_PATH


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
def index():
    movies = Movies.query.filter(Movies.is_del==False).order_by('-create_time')

    items = []
    for movie in movies:
        item={
            "name":movie.name,
            "url":url_for('detail',path=movie.detail_path),
            "photo_url":"ddd/%s/%s" % (movie.detail_path,movie.photo_path)
        }
        items.append(item)

    return render_template('index.html', items=items)


@app.route('/detail/<path>/')
def detail(path):
    host = request.headers.get('Host')

    photo_list = []
    for file in find_file(os.path.join(RESOURCE_PATH,path),'.jpg'):
        photo_list.append("//{0}/ddd/{1}/{2}".format(host, path, file).replace('\\','/'))

    movie_list = []
    for file in find_file(os.path.join(RESOURCE_PATH, path), '.mp4'):
        movie_list.append("//{0}/ddd/{1}/{2}".format(host, path, file).replace('\\', '/'))

    detail = {
        "photos":photo_list,
        "movies":movie_list
    }

    try:
        detail['movies'].sort(reverse=True)
        detail['title'] = os.path.basename(detail['movies'][0])
    except:
        detail['title'] = u"未找到文件名"

    return render_template('detail.html',detail=detail)

@app.route('/update/')
def update():
    scan_local_path()
    return u"本地数据扫描完毕。"


@app.route('/hello/')
def hello():
    return render_template('hello.html')


if __name__ == '__main__':
    app.run()
