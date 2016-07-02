# -*- coding: utf8 -*-
u'''
@summary:
@author: cshanxiao
@date: 2016年7月3日
'''
import logging.config
from hunter.common.config import LOG_CONFIG_FILE_PATH


logging.config.fileConfig(LOG_CONFIG_FILE_PATH)
log = logging.getLogger("root")
dytt8log = logging.getLogger("dytt8_log")



