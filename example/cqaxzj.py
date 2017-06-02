#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
from pymongo import MongoClient
from readability.readability import Document
from currency_craler.all_web_crawler import News
import re
import chardet
client = MongoClient()
co = client['all_web']['qjyc_cqzj_gov_cn']


class GovCrawler(News):
    def parser_content(self, html, index_url):
        print index_url
        import pdb
        html = re.sub('<select[\s\S]+?</select>', '', html)
        readable_article = Document(html)
        content = readable_article.summary()
        title = readable_article.title()
        time_search = re.search("发布时间.{20}",html)
        # if u'发布日期' in content :
        #      pdb.set_trace()
        if time_search:
            push_time = self.parser_match_time(time_search.group())
        else:
            push_time = self.parser_html_time(html)
        print "*" * 100
        print push_time

        self.SAVECO.update({"url": index_url}, {"url": index_url, "html": content, "time": push_time, "title": title},
                  upsert=True)


yongcuan = GovCrawler('http://qjyc.cqzj.gov.cn/ZJ_Page/Content.aspx?newsid=30327', 100)
yongcuan.start()

#无法提取时间