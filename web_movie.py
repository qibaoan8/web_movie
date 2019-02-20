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
from urllib import unquote
from base.find_file import find_file, find_file_keys
from base.update_db import scan_local_path
from exts import db
from models import Movies
from sqlalchemy import or_
from config import RESOURCE_PATH


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
@app.route('/index/')
def index():
    score = request.args.get('score')
    score = 0 if not score else int(score)
    # if not score: score = 0
    movies = Movies.query.filter(Movies.is_del==False, Movies.score==score).order_by('-create_time')

    items = []
    for movie in movies:
        item={
            "name":movie.name,
            "url":url_for('detail',path=movie.detail_path),
            "photo_url":"/ddd/%s/%s" % (movie.detail_path,movie.photo_path)
        }
        items.append(item)

    index = {
        'photos':items,
        'score_list':range(0,6),
        'score':score,
    }

    return render_template('index.html', index=index)


@app.route('/detail/<path>/')
def detail(path):

    photo_list = []
    for file in find_file_keys(os.path.join(RESOURCE_PATH,path),config.PHOTO_FORMANT):
        photo_list.append("/ddd/{0}/{1}".format(path, file).replace('\\','/'))

    movie_list = []
    for file in find_file_keys(os.path.join(RESOURCE_PATH, path), config.MOVIE_FORMANT):
        movie_list.append("/ddd/{0}/{1}".format(path, file).replace('\\', '/'))
    movie = Movies.query.filter(Movies.detail_path == path).first()


    detail = {
        "photos":photo_list,
        "movies":movie_list
    }
    detail['score_list'] = range(0,6)
    detail['score'] = movie.score

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

@app.route('/update_collection_score/',methods=['POST'])
def update_collection_score():
    # update_collection_score_func()
    detail_path = unquote(request.form.get('path'))
    movie_score = request.form.get('score')
    movie = Movies.query.filter(Movies.detail_path==detail_path).first()
    movie.score = movie_score
    db.session.commit()
    return "ok"

@app.route('/hello/')
def hello():
    return render_template('hello.html')


if __name__ == '__main__':
    app.run()
