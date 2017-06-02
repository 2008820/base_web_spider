#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
import re
import time
import requests
import traceback

def try_number(num, second):
    def _func(func):
        def __func(*args, **kwargs):
            loop = 0
            while 1:
                loop += 1
                try:
                    return func(*args, **kwargs)
                except:
                    print traceback.print_exc()
                    time.sleep(second)
                    if loop == num:
                        return ''
                        pass

        return __func

    return _func


class crawler():  # 抓去模块
    """
    try_number 尝试次数
    head_dict 清洗头部成字典
    cookie_dict 清洗cookie 成字典
    curl 用 自带 session 访问
    noncurl 用 requests 访问

    """
    s = requests.session()

    @staticmethod
    def head_dict(head):
        res_dict = {}
        for item in head.splitlines():
            if item:
                temp_data = item.split(':')
                res_dict[temp_data[0]] = temp_data[1]
        return res_dict

    def cookie_dict(self, cookie):
        listData = cookie.strip().split(';')
        temp_dict = {}
        for line in listData:
            line = line.strip()
            temp_data = line.split('=')
            # print temp_data
            temp_dict[temp_data[0]] = temp_data[1]
        return temp_dict
    @try_number(5,10)
    def curl(self, url, data='', **kwargs):
        if data:
            return self.s.post(url, timeout=30, data=data, **kwargs)
        else:
            return self.s.get(url, **kwargs)
    @try_number(5, 10)
    def noncurl(self, url, data='',  **kwargs):
        if data:
            return requests.post(url, timeout=30, data=data, **kwargs)
        else:
            return requests.get(url, timeout=30, **kwargs)
