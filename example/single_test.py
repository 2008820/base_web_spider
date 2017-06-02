from currency_craler.all_web_crawler import News
from pyboy.xcrawler import crawler
curl = crawler()
class Baoda(News):
    def __init__(self, index_url):
        News.__init__(self, index_url)
        head_str = '''
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Encoding:gzip, deflate, sdch
Accept-Language:zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4
Cache-Control:max-age=0
Connection:keep-alive
Cookie:scb-user-token=82d038c549a70fe1d19689f3fc44c3369bbe9853cca9ca4a54b570a84227bd1a50f8164509a70a9a0cbeba5d18b4eb562a5dbeac3a0b59e3329e2d98edcb6162
Host:test.baoda8.com
If-None-Match:W/"2f12-JlundYmEWU8qYzMXf12vlg"
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36
'''
        self.head = curl.head_dict(self.head_str)
        self.head['Host'] = self.host
    def parser_content(self,html,url):
        print html
        print url

baodao = Baoda('http://test.baoda8.com/report/efdd54fbe5048d2bfb7db15cb6ada03388e05a498e2eba7f74b74384782ac9bb')
baodao.start()