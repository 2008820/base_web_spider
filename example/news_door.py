#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
import re
import hashlib
import datetime
from readability.readability import Document
import psycopg2
import psycopg2.extras
from psycopg2 import IntegrityError
from currency_craler import all_web_crawler, html_template


class door_news(all_web_crawler.News):
    def __init__(self, source, index_url, pools, url_needs_reg):
        all_web_crawler.News.__init__(self, index_url, pools=0, url_distinct_model='mongo', init_url=1)
        self.url_needs_reg = url_needs_reg
        self.all_curl_num = 0
        self.source = source
        self.conn_status = psycopg2.connect(database="distinct_news_test", user="news_test", password="1qaz2wsx",
                                            host="192.168.31.157")
        self.conn_content = psycopg2.connect(database="distinct_news_test", user="news_test", password="1qaz2wsx",
                                             host="192.168.31.157")

    def _get_sentence_hash(self, html):
        text = re.sub('<.+?>', '', html)
        if not text:
            return '', ''
        text = re.sub('[ \t\n]', '', text)
        sentence = re.split(u'[。\?？！\!，、：]', text)
        sentence.sort(key=lambda x: len(x), reverse=True)
        hash_key = ''.join(sentence[0:3])
        return hashlib.md5(hash_key).hexdigest(), text

    def _news_status_json(self):
        return {"url": "", "published_time": "", "source": self.source, "title": "", "content_id": ""}

    def parser_content(self, html, index_url):
        print self.targets
        if self.all_curl_num >= 1000:
            self.targets = []
        if 'list' in index_url:
            return
        readable_article = Document(html).summary()
        push_time = self.parser_html_time(html)
        if not push_time or '2017-04-18' not in push_time:
            return
        try:
            title = re.findall('<h1.*?>(.+?)</h1>', html)[0]
            title = re.sub('<.+?>', '', title)
        except:
            print 'no-h1' + index_url
            return ''
        self.all_curl_num += 1
        content_id = self._content_hash_id(readable_article)
        print content_id
        if not content_id:
            return
        print '*' * 100
        cur = self.conn_status.cursor()
        sql = 'insert into news_status(url, published_time, title, source,content_id) VALUES (%s,%s,%s,%s,%s)'
        sql_arg = (index_url, push_time, title, self.source, content_id)
        print cur.mogrify(sql, sql_arg)
        # raw_input('go on')
        try:
            cur.execute(sql, sql_arg)
            print self.conn_status.commit()
            print index_url
        except Exception, e:
            print e
            self.conn_status.rollback()
        finally:
            cur.close()

    def _content_hash_id(self, html):
        hash_value, text = self._get_sentence_hash(html)
        if not hash_value:
            return
        cur = self.conn_content.cursor()
        sql = "insert into news_content(abstract, content, hash, text) VALUES (%s,%s,%s,%s) returning id;"
        sql_arg = (text[0:15], html, hash_value, text)
        try:
            cur.execute(sql, sql_arg)
            self.conn_content.commit()
            id_of_new_row = cur.fetchone()[0]
            content_id = id_of_new_row
        except IntegrityError:
            self.conn_content.rollback()
            sql = "select id from news_content where hash='%s'" % hash_value
            cur.execute(sql)
            content_id = cur.fetchone()[0]
        finally:
            cur.close()

        return content_id


news_site_list = [
    {"source": "163", "index_url": "http://news.163.com/", "pools": 0, "url_needs_reg": ['17/0418', 'html$']},
    {"source": "sohu", "index_url": "http://news.sohu.com/", "pools": 50, "url_needs_reg": ['/a/', '\d$']},
    {"source": "ifeng", "index_url": "http://news.ifeng.com/", "pools": 50, "url_needs_reg": ['/a/20170418/', 'shtml$']},
    {"source": "qq", "index_url": "http://news.qq.com/", "pools": 50, "url_needs_reg": ['/a/20170418/', 'htm$']},
    {"source": "xinhuanet", "index_url": "http://www.xinhuanet.com/", "pools": 50, "url_needs_reg": ['/2017-04/18', 'htm$']},
    {"source": "www_thepaper_cn", "index_url": "http://www.thepaper.cn/", "pools": 50, "url_needs_reg": ['newsDetail_forward_', '\d$']},
    {"source": "www_people.com_cn", "index_url": "http://www.people.com.cn/", "pools": 50, "url_needs_reg": ['2017/0418', 'html$']},
    {"source": "www_chinanews_com", "index_url": "http://www.chinanews.com/", "pools": 50, "url_needs_reg": ['2017/04-18', 'shtml$']},
    {"source": "www_huanqiu_com/", "index_url": "http://www.huanqiu.com/", "pools": 50, "url_needs_reg": ['/a/20170418/', 'htm$']},
    {"source": "www_cankaoxiaoxi_com", "index_url": "http://www.cankaoxiaoxi.com/", "pools": 50, "url_needs_reg": ['/20170418/', 'shtml$']}

    ]

for news_site in news_site_list:
    news360 = door_news(news_site['source'], news_site['index_url'], news_site['pools'], news_site['url_needs_reg'])
    news360.start()

# html = html_template.html
# news360.parser_content(html,'http://sh.qihoo.com/')
# {"source": "qq", "index_url":"http://mil.qq.com/mil_index.htm", "pools":50, "url_needs_reg":['/a/', 'htm$']}
