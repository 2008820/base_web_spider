from currency_craler.all_web_crawler import News
from readability.readability import Document
from pymongo import MongoClient
client = MongoClient()
co = client['all_web']['cqyc']


class GovCrawler(News):
     def parser_content(self, html, index_url):
         print index_url
         readable_article = Document(html).summary()
         push_time = self.parser_html_time(html)

         co.update({"url": index_url}, {"url": index_url, "html": readable_article, "time": push_time}, upsert=True)

yongcuan = GovCrawler('http://bbs.cqyc.net/forum-30-1.html', 100)

yongcuan.start()
# http://qw.cqyc.gov.cn/art/2012/10/26/art_601_26354.html
# http://qw.cqyc.gov.cn/art/2016/12/1/art_516_164982.html