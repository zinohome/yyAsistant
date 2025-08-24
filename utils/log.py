#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: VACDA

import os
import sys

from loguru import logger as log
from configs.base_config import BaseConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, BaseConfig.app_log_filename)

# 清除Loguru默认处理器（关键修复）
log.remove()
log.add(LOG_PATH,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        rotation="100 MB",
        retention="14 days",
        level=BaseConfig.app_log_level,
        enqueue=True)
log.add(sys.stdout,
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            colorize=True,
            level=BaseConfig.app_log_level,
            enqueue=True)

if __name__ == '__main__':
    log.success('[测试log] hello, world')
    log.info('[测试log] hello, world')
    log.debug('[测试log] hello, world')
    log.warning('[测试log] hello, world')
    log.error('[测试log] hello, world')
    log.critical('[测试log] hello, world')
    #log.exception('[测试log] hello, world')