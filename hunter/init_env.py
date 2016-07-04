# -*- coding: utf8 -*-
u'''
@summary:
@author: cshanxiao
@date: 2016年7月4日
'''
import os


def init_env():
    logs_path = "./data/logs"
    tmp_path = "./data/tmp"
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
    
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

init_env()