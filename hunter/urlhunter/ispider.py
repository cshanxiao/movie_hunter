# -*- coding: utf8 -*-
u'''
@summary:
@author: cshanxiao
@date: 2016年7月3日
'''
import random
import time

import requests


class ISpider(object):

    def __init__(self):
        self.base_url = ""
        self.sess = requests.session()
    
    def random_delay_get(self, url, **kargs):
        time.sleep(random.randint(0, 10))
        return self.sess.get(url, **kargs)
    
    