#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
from readability.readability import Document
from currency_craler.all_web_crawler import News
import re
import chardet
from pyquery import PyQuery
import datetime
import traceback

class GovCrawler(News):
    def parser_content(self, html, index_url):
        print index_url
        import pdb
        if 'charset=gb2312' in html:
            try:
                code = chardet.detect(html)['encoding']
                html = html.decode(code, 'ignore')
            except:
                pass
        html = re.sub('<select[\s\S]+?</select>', '', html)
        readable_article = Document(html)
        content = readable_article.summary()
        content = re.sub('</?div.*?>', '', content)
        title = readable_article.title()
        time_search = re.search("发布时间.{20}",html)
        # if u'发布日期' in content :
        #      pdb.set_trace()
        if time_search:
            push_time = self.parser_match_time(time_search.group())
        else:
            try:
                push_time = self.parser_html_time(html)
            except:
                push_time = ''
        text = PyQuery(readable_article).text()
        print "*" * 100
        print push_time
        self.SAVECO.update({"url": index_url}, {"url": index_url, "html": content, "text": text, "time": push_time, "title": title,
                                                "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                  upsert=True)


yongcuan = GovCrawler('http://news.ycw.gov.cn/index.html', 100, url_distinct_model='mongo')
yongcuan.start()