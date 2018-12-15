#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: models.py
Date: 2018-12-01 17:39
Author: wang.gaofei@alibaba-inc.com 
"""

# 专门存放数据库模型的，比如表

from exts import db
from datetime import datetime

class Movies(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    create_time = db.Column(db.DATETIME, default=datetime.now)
    name = db.Column(db.String(1024),nullable=False)
    detail_path = db.Column(db.String(100),nullable=False)
    photo_path = db.Column(db.String(100),nullable=False)
    is_del = db.Column(db.Boolean,default=False)
    is_collection = db.Column(db.Boolean,default=False)



