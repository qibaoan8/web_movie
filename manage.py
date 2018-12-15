#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: manage.py
Date: 2018-12-01 17:39
Author: wang.gaofei@alibaba-inc.com 
"""

#  专门用来存放表的创建的命令的
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from web_movie import app
from exts import db
from models import Movies


manager = Manager(app)

# 使用Migrate绑定app和db
migrate = Migrate(app,db)

# 添加迁移脚本的命令到mananger
manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    manager.run()




