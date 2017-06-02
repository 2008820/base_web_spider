#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
import chardet
import copy
import re
import time
import traceback
import urlparse

import gevent
from bs4 import BeautifulSoup
from pymongo import MongoClient

from util.time_parser import parse_time
from util.xcrawler import crawler

# monkey.patch_all()
curl = crawler()

client = MongoClient()
DB = client['urlpool']
SAVE_DB = client['all_web']


# 判断新闻首页是否需要更新
# def index_is_update(html, host):
#     html_hash = hashlib.sha1(html).hexdigest()
#     index_db = CO.find_one({'url': host})
#     if index_db:
#         if index_db['hash'] != html_hash:
#             CO.update_one({'url': host}, {"url": host, "hash": html_hash})
#             return False
#         else:
#             return True
#     else:
#         CO.update_one({'url': host}, {"url": host, "hash": html_hash})
#         return False




class News(object):
    def __init__(self, index_url, pools=0, url_distinct_model='', init_url=0):
        """
         如果网站链接有上百万,请开启 url_distinct_model == mongo, 默认是保存在内存里
         parser_content  FUNC 函数是解析单个网页的
         url_needs_reg   LIST 写正则表达式，写你需要的url
         pools         INT 开启异步线程
         head_str      STR 浏览器中的header,直接复制粘贴即可
         url_filter_character     LIST  排除url里不要的参数

        """

        self.targets = set()
        self.visited = {}
        self.head_str = '''
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language:zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4
Cache-Control:max-age=0
Connection:keep-alive
Host:spider
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
'''
        self.url_filter_model = url_distinct_model
        self.url_needs_reg = []
        url_analy = urlparse.urlparse(index_url)
        self.pools = pools
        self.head = curl.head_dict(self.head_str)
        self.index_url = index_url
        self.host = url_analy.netloc
        self.head['Host'] = self.host
        self.scheme = url_analy.scheme + '://' + self.host
        self.CO = DB[self.host.replace('.', '_')]
        self.SAVECO = SAVE_DB[self.host.replace('.', '_')]
        if init_url:
            self.CO.drop()
        self.url_filter_character = ['.css', '.js', '.jpg', '.png', '#', '.xls', '.doc', 'javascript']


    def _need_url(self,link):
        url_rules_list = copy.deepcopy(self.url_needs_reg)
        while 1:
            if url_rules_list:
                rules = url_rules_list.pop()
                if re.search(rules, link):
                    continue
                else:
                    return
            else:
                return link

    def analysis_page(self, html, target_url=''):
        soup = BeautifulSoup(html, "html.parser")
        list_a = [i.get('href') for i in soup.find_all('a') if i.get('href')]
        self.parser_content(html, target_url)
        if self.url_needs_reg:
            if target_url:
                _list_a = filter(self._need_url, list_a)
                map(self.add_url, _list_a)
                map(self.add_visited_url, [i for i in list_a if i not in _list_a])
            self.filter_inlink(_list_a, target_url)
        else:
            self.filter_inlink(list_a, target_url)
        self.add_visited_url(target_url)
    # 判断网页编码
    def _judge_html_code(self, html):
        try:
            code = chardet.detect(html)['encoding']
            html = html.decode(code, 'ignore')
        except:
            pass
        return html

    # 解析网页时间
    def parser_html_time(self, html):
        body = re.findall('<body[\s\S]*?>([\s\S]+)', html)
        if body:
            body = body[0]
            body = re.sub("<script[\s\S]+?</script>", "", body)
            body = re.sub('</?[\s\S]*?>', '', body)
        else:
            body = ''
        return parse_time(body)

    def parser_match_time(self, timestamp):
        return parse_time(timestamp)

    # 解析符合要求的,并入库
    def parser_content(self, html, index_url):
        print self.targets
        pass
    
    def add_visited_url(self, url):
        if self.url_filter_model == 'mongo':
            if self.CO.find_one({"url": url}):
                return False
            else:
                self.CO.insert({"url": url})
                return True
        else:
            if not self.visited.get(url, False):
                self.visited[url] = True
                return True
            else:
                return False
    # 加入爬取目标
    def add_url(self, url):
        if self.add_visited_url(url):
            self.targets.add(url)

    def distinct_url_mongodb(self, url):
        if self.CO.find_one({"url": url}):
            return
        else:
            self.CO.insert({"url": url})
            self.targets.add(url)

    def url_select(self, url):
        if not self.url_needs_reg:
            return True
        for reg in self.url_needs_reg:
            if re.search(reg, url):
                return True
        return False

    def filter_inlink(self, url_list, root_url):
        # clean_url = [i for i in url_list for j in self.url_filter_character if j not in i]
        clean_url = list()
        def _is_match(url):
            for term in self.url_filter_character:
                if term in url:
                    return None
            return url
        clean_url_status = filter(_is_match, url_list)
        clean_url = list(set(clean_url_status))
        for _url in clean_url:
            try:
                _urlanaly = urlparse.urlparse(_url)
            except:
                continue
            if not _urlanaly.netloc:
                if _url[0] != '/':
                    if _url[:2] == '..':
                        url = '/'.join(root_url.split('/')[:-2])
                        url = url + _url.replace('..', '')
                    else:
                        del_parat = root_url.split('/')[-1]
                        relative_url = root_url.replace(del_parat, '')
                        url = relative_url + _url
                    # raw_input(url + '\n go on')
                else:
                    url = self.scheme + _url
            elif _urlanaly.netloc == self.host:
                url = _url
            else:
                continue

            if not self.url_select(url):
                continue
            if not self.add_visited_url(url):
                continue
            self.add_url(url)


    def curl_page(self):
        while self.targets:
            url = self.targets.pop()
            try:
                self._curl_get(url)
                # co.insert_one({"url": url})
            except Exception, e:
                print traceback.print_exc()
                print e
                continue

    def _curl_get(self, url):
        response = curl.curl(url, headers=self.head)
        # print response.content
        html_code = response.headers['Content-Type']
        if response.status_code != 200:
            print url
            print response.status_code
            print 'timesleep'
            time.sleep(10)
            response = curl.curl(url, headers=self.head)
        html = response.content
        if "GBK" in html_code or 'charset=gb2312' in html:
           html = self._judge_html_code(html)
        self.analysis_page(html, url)

    def _pool_gevent(self):
        list_pool = []
        for pool in xrange(self.pools):
            list_pool.append(gevent.spawn(self.curl_page))
        gevent.joinall(list_pool)

    def start(self):
        req = curl.curl(self.index_url, headers=self.head)
        html = req.content
        html_code = req.headers['Content-Type']
        # open('temp.html', 'w').write(html)
        if "GBK" in html_code or 'charset=gb2312' in html:
           html = self._judge_html_code(html)
        self.analysis_page(html, self.index_url)
        if self.pools:
            print '1'*100
            self._pool_gevent()
        else:
            self.curl_page()


if __name__ == '__main__':
    p2p = News('http://python.jobbole.com/', 50, url_distinct_model='mongo', init_url=1)
    p2p.start()
