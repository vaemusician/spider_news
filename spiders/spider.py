# -*- coding:utf-8 -*-
import json
import time
from hashlib import md5

import requests
from dateutil.parser import parse
from faker import Faker
from goose3 import Goose, Configuration
from goose3.text import StopWordsChinese

from spiders.decorators import *


class Spider:
    def __init__(self, req_params):
        self.req_params = req_params
        self.task_msg = req_params['task_msg']
        self.proxy = req_params['proxy']
        self.method = req_params['method']
        self.source = ''
        self.result = dict(msg_type='scraped_data',
                           task_msg=self.task_msg,
                           result=dict(
                               dtype='news',
                               item=dict(),
                           ),
                           )
        fake = Faker()
        self.ua = fake.user_agent()

    # news
    @request_check
    def get_news_last_list(self):
        pass

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        pass

    def crawling_news(self):
        pass

    # search
    @request_check
    def get_search_result(self):
        pass

    @analyze_check
    def analyze_search_result(self, search_result_text):
        pass

    def crawling_search(self):
        pass

    # registered
    def crawling_reg(self):
        pass

    def crawling(self):
        method = {
            'news': self.crawling_news,
            'search': self.crawling_search,
            'reg': self.crawling_reg,
        }
        method[self.method]()

    @request_check
    def auto_news_main_content(self, news_url, keyword=''):
        config = Configuration()
        config.http_proxies = {
            'http': self.proxy,
            'https': self.proxy
        }
        config.browser_user_agent = self.ua
        config.stopwords_class = StopWordsChinese
        config.http_proxies = {
            'http': self.proxy,
            'https': self.proxy
        }
        g = Goose(config)
        article = g.extract(news_url)
        news_post = dict(
            doc_id=md5(article.final_url.encode('utf-8')).hexdigest(),
            keyword=keyword,
            url=article.final_url,
            title=article.title,
            platform='news',
            content=article.cleaned_text,
            author=article.authors,
            source= self.source if self.source else article.domain,
            published_time=int(parse(article.publish_date).timestamp() * 1000) if article.publish_date else None,
            spi_time=int(time.time() * 1000)
        )
        return news_post

    @staticmethod
    def check_phone_num(phone):
        start_time = time.time()
        data = {
            'phone_num': phone
        }
        flag = False
        while True:
            res = requests.post('http://129.226.169.195:9989/api/sms/check_phone_num', json=data)
            resjs = json.loads(res.text)
            if resjs['code'] == 0:
                flag = True
                break
            if resjs['code'] == 1703001:  # 等待可用
                pass
            check_time = time.time()
            end_time = check_time - start_time
            if end_time >= 60 * 10 or resjs['code'] == 1703002:  # 10 min
                requests.post('http://129.226.169.195:9989/api/sms/unlock', json=data)  # 结束，调用释放
                break
        return flag

    @staticmethod
    def get_verify_polling(phone):
        start_time = time.time()
        data = {
            'phone_num': phone
        }
        verify = ''
        restask = json.loads(
            requests.post('http://129.226.169.195:9989/api/sms/get_task_id', json=data).text)  # get task_id
        if restask['code'] == 0:
            task_id = restask['task_id']
            while True:  # 根据task_id get verify
                data_polling = {
                    'task_id': task_id
                }
                code = json.loads(
                    requests.post('http://129.226.169.195:9989/api/sms/get_verify_polling', json=data_polling).text)
                if code['code'] == 0:
                    verify = code['verify']
                    break
                check_time = time.time()
                end_time = check_time - start_time
                if end_time >= 60 * 10:  # 10 min
                    break
        requests.post('http://129.226.169.195:9989/api/sms/unlock', json=data)
        return verify

    @staticmethod
    def sms_unlock(phone):
        data = {
            'phone_num': phone
        }
        requests.post('http://129.226.169.195:9989/api/sms/unlock', json=data)
