#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
from readability.readability import Document
from base_temp.all_web_es import News
import re
from bs4 import BeautifulSoup
import chardet
from pyquery import PyQuery
import datetime


class BBS(News):
    def __init__(self, index_url):
        News.__init__(self, index_url, pools=100, url_distinct_model='mongo')
        # self.url_needs_reg = ['forum-2-', 'thread-\d{7}-1-']
    def parser_content(self, html, index_url):
        import pdb
        soup = BeautifulSoup(html, "html.parser")
        open('temp.html', 'w').write(html)
        title = soup.find("title").get_text()
        first_note = soup.find("div", attrs={"class": "t_fsz"})
        html = str(first_note)
        try:
            text = first_note.get_text(strip=True)
        except:
            return
        push_time = soup.find("em", id=re.compile("authorposton")).get_text()
        push_time = self.parser_match_time(push_time)

        # raw_input('go on')
        # print content
        print index_url
        # print self.SAVECO.update({"url": index_url}, {"url": index_url, "html": html, "text": text, "time": push_time, "title": title,
        #                                         "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, upsert=True)
        # print self.SAVECO.insert_one({"url": index_url, "html": html, "text": text, "time": push_time, "title": title,
        #                                         "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        print "*" * 100
        print push_time
        # import pdb
        # pdb.set_trace()
        data = {"url": index_url, "html": html.replace('\n', ''), "text": text.replace('\n', ''), "title": title, "pubulish_time": push_time,"created_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
        print self.save_es.insert(index_url, data)
        # raw_input('go on')

yongcuan_bbs = BBS('http://finance.qq.com/a/20170606/039580.htm')
yongcuan_bbs.start()