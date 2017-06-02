#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
解析各种时间字符串到时间对象或者标准字符串格式
"""

import re
import sys
import time
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")

# 标准时间格式
STARDAND_FORMAT = '%Y-%m-%d %H:%M:%S'
# 中文数字
CHINESE_NUMS = u'〇一二三四五六七八九十'
# 纯数字格式
PATTERN_NUMBER_TIME = re.compile(ur'\d{8}')
# 标准时间格式的正则
PATTERN_STARDAND_TIME = re.compile(ur'\d{4}-\d{2}-\d{2} ?\d{0,2}:?\d{0,2}:?\d{0,2}')
# 标准时间年月日
PATTERN_CHINESE_CHAR = re.compile(ur'(\d+?)年(\d+?)月(\d+?)日')

# 中文时间格式的正则
PATTERN_CHINESE_TIME = re.compile(ur'([%s]{4})年([%s]+)月([%s]+)日' % (CHINESE_NUMS, CHINESE_NUMS, CHINESE_NUMS))
# 其它时间格式的正则
PATTERN_GENERAL_TIME = re.compile(ur'(\d{4})[^\d](\d{1,2})[^\d](\d{1,2})[^\d]?(\d{1,2})?:?(\d{1,2})?:?(\d{1,2})?')
# 时间表达式的正则
PATTERN_TIME_EXPRESSION = re.compile(ur'(\d+)[小|个]?(年|季度|月|周|天|日|时|分|秒)[钟]?[以|之]?(前|后)')

# 函数： 去除杂质
_IMPURITY_CLEAR_FUNCTION_LIST = [
    lambda string: re.sub(ur'日|号', '', string),
    lambda string: re.sub(ur'点|时|分', ':', string),
]

# 时间与关键字的对应关系
_KEY_TIME_MAPPING = {
    u'年': 31536000, u'季度': 7862400, u'月': 2592000, u'周': 604800,
    u'天': 86400, u'日': 86400, u'时': 3600, u'分': 60, u'秒': 1
}


def _parse_chinese_field(field):
    field = ''.join(map(lambda x: str(CHINESE_NUMS.find(x)), field))
    return int(field[0] + field[-1] if len(field) > 2 else field)


def _build_str_from_chinese(chinese_items):
    """
    根据解析出的中文时间字符串的关键字返回对应的标准格式字符串
    """
    year, month, day = chinese_items
    year = reduce(lambda a, b: a*10+b, map(CHINESE_NUMS.find, year))
    return '%04d-%02d-%02d 00:00:00' % (year, _parse_chinese_field(month), _parse_chinese_field(day))


def _build_str_from_expression(exp_items):
    """
    根据解析出的时间表达式的关键字计算对应的表达式值
    :return: 表达式对应时间的标准时间格式字符串表示形式
    """
    time_delta_base, unit, method = exp_items
    if unit not in _KEY_TIME_MAPPING:
        return None
    delta = datetime.timedelta(seconds=int(time_delta_base) * _KEY_TIME_MAPPING[unit])
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now + (delta, -delta)[u'前' == method], STARDAND_FORMAT)


def _build_str_from_time_items(items):
    """
    根据解析出的时间字符串关键字计算标准时间表示格式的字符串
    :return: 标准时间格式字符串表示形式
    """
    if not items:
        return None
    items = [int(item) for item in items if item]
    items = items + [0 for _ in xrange(6-len(items))]
    return '%d-%02d-%02d %02d:%02d:%02d' % (items[0], items[1], items[2], items[3], items[4], items[5])


def _build_str_from_number(time_str):
    year, month, day = map(int, [time_str[:4], time_str[4:6], time_str[-2:]])
    if 1 <= month <= 12 and 1 <= day <= 31:
        return '%04d-%02d-%02d 00:00:00' % (year, month, day)
    print 'dddddd'
    return None


def _parse_time(time_str):
    # check argument
    if not isinstance(time_str, basestring):
        raise ValueError('time_str must be a string(include str and unicode), got %s' % type(time_str))

    # convert to unicode string
    if not isinstance(time_str, unicode):
        time_str = unicode(time_str)

    # 如果包含标准字符串形式
    if PATTERN_STARDAND_TIME.search(time_str):
        return PATTERN_STARDAND_TIME.findall(time_str)[0]

    # 中文字，数字正常
    if PATTERN_CHINESE_CHAR.search(time_str):
         all_time = PATTERN_CHINESE_CHAR.findall(time_str)[0]
         return '-'.join(all_time) +' ' + '00:00:00'

    time_str = time_str.replace(u'零', u'〇')
    if PATTERN_CHINESE_TIME.search(time_str):
        return _build_str_from_chinese(PATTERN_CHINESE_TIME.findall(time_str)[0])

     # 查找时间
    if PATTERN_GENERAL_TIME.search(time_str):
        return _build_str_from_time_items(PATTERN_GENERAL_TIME.findall(time_str)[0])



    # 纯数字格式
    if PATTERN_NUMBER_TIME.search(time_str):
        r = _build_str_from_number(PATTERN_NUMBER_TIME.findall(time_str)[0])
        if r:
            return r

    # 如果是时间表达式（3个月以前，2年后...）
    if PATTERN_TIME_EXPRESSION.search(time_str):
        return _build_str_from_expression(PATTERN_TIME_EXPRESSION.findall(time_str)[0])



    # 去除杂质
    for func in _IMPURITY_CLEAR_FUNCTION_LIST:
        time_str = func(time_str)

    return None


def parse_time(time_str, iso_time_obj=False):
    """
    解析出一个字符串中包含的（第一个）时间，并转换为时间对象或者字符串表现形式
    :param time_str: 时间字符串 （eg. "2012年7月9日"， "2012-03-01"， "2016.05.1 12:11:11"， "5小时以前"，"5天后"）
    :param iso_time_obj: True => 转换为对象 | False => 转换为字符串 | default value: False
    :return: datetime object or time string
    """
    time_str = _parse_time(time_str)
    if not time_str:
        return ""
    if iso_time_obj:
        return datetime.datetime.strptime(time_str, STARDAND_FORMAT)
    return time_str


def now(obj=True, utc=False, precise=False):
    """
    得到此刻的时间
    """
    t = (datetime.datetime.now(), datetime.datetime.utcnow())[utc]
    return (t.strftime(STARDAND_FORMAT + ('', '.%f')[precise]), t)[obj]


if __name__ == '__main__':
    from all_web_crawler import News
    test_parser = News('http://www.baidu.com')

    # print now(obj=False, precise=True)
    time_text = open('time_test.text').read()
    # print parse_time(time_text)
    print test_parser.parser_html_time(time_text)
    # print parse_time("发布日期：2012-10-22")