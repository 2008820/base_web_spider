#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
import requests
import urllib
import json


class ES():
    def __init__(self, host, index, doc_type, port='9200'):
        if host.startswith('http'):
            self.host = host
        else:
            self.host = 'http://' + host
        self.port=port
        self.index = index
        self.doc_type = doc_type

        self.url = self.host + ':' + port + '/' + self.index + '/' + self.doc_type + '/'
        self.update_url = "{host}%s/_update".format(host=self.url)
        self.index_url = "{host}%s".format(host=self.url)

    def judge(self, _id):
        if '/' in _id:
            _id = urllib.quote_plus(_id)
        return _id

    def format(self, data):
        if isinstance(data, dict):
            return json.dumps(data)
        if isinstance(data, list):
            return json.dumps(data)
        else:
            return data

    # 强制插入
    def insert(self, _id, data):
        _id = self.judge(_id)
        # print self.format(data)
        res = requests.put(self.index_url % _id, self.format(data))
        return self.replay(res)

    def bulk_insert(self, data):
        pass

    def replay(self, response):
        if str(response.status_code)[0] != 2:
            return response.content
        return response

    def get(self, _id):
        _id = self.judge(_id)
        res = requests.get(self.index_url % _id).json()
        return res['found']

    # id 存在就更新，否则插入
    def update_or_create(self, _id, data):
        _id = self.judge(_id)
        data = self.format(data)
        post_data = '{"doc": %s, "upsert":%s}' % (data, data)
        response = requests.post(self.update_url % _id, data=post_data)
        return self.replay(response)

    def delete(self, _id):
        _id = self.judge(_id)
        res = requests.delete(self.index_url % _id)
        return self.replay(res)

    def search(self):
        data = {"query": {"bool": {"must": {'range': {"pubulish_time": {"gte": "2016-12-20"}}}}}}
        res = requests.post(self.url + '_search?', self.format(data))
        return self.replay(res)

    def delete_type(self):
        data = '{"query": {"match_all": {}}}'
        res = requests.post(self.url + '_delete_by_query', data=data)
        return self.replay(res)

    def alter_mapping(self, field):
        data = {
          self.doc_type: {
              "properties": {
                field: {
                  "type":   "date",
                  "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||yyyy-MM-dd HH:mm||epoch_millis"
                }
              }
            }
          }
        map_url = self.host + ':' + self.port + '/' + self.index + '/' + self.doc_type + '/' + '_mapping?pretty'
        print map_url
        res = requests.post(map_url, data=self.format(data))
        return self.replay(res)

    def delete_index(self):
        delete_url = self.host + ':' +self.port + '/' + self.index
        print delete_url
        res = requests.delete(delete_url)
        return self.replay(res)



if __name__ == '__main__':
    news_es = ES(host='http://192.168.31.114', index="test_news", doc_type="news")
    print news_es.search('')

