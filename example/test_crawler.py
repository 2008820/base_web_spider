from pymongo import MongoClient
from readability.readability import Document

from currency_craler.all_web_crawler import News

client = MongoClient()
co = client['all_web']['wangdaicaifu']

# co.ensure_index('url', unique=True)

class wangdaicaifu(News):
    def __init__(self, index_url, pools=0, url_distinct_model='', init_url=0):
        News.__init__(self, index_url, pools, url_distinct_model, init_url)
        self.url_needs_reg = ['alist', 'aview']

    def parser_content(self, html, index_url):

        readable_article = Document(html).summary()

        push_time = self.parser_html_time(html)
        print co.update({"url": index_url}, {"url": index_url, "html": readable_article, "time": push_time}, upsert=True)

artcle = wangdaicaifu('http://www.wangdaicaifu.com/Home/Cms/alist.html', 10, url_distinct_model='mongo', init_url=1)
artcle.start()
