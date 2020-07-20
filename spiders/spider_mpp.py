import json
import time

import requests
from lxml import etree

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y 民众日报（台湾）
class MppSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'http://www.mypeople.tw/'
        self.source_url = 'http://www.mypeople.tw/'
        self.cookie = ''

    @request_check
    def get_cookie(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'http://www.mypeople.tw/'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        cookies = requests.utils.dict_from_cookiejar(wb_res.cookies)
        for key in cookies.keys():
            self.cookie = str(key) + '=' + str(cookies.get(key))

    # news
    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        head['Cookie'] = self.cookie
        # 今日新闻焦点
        wb_url = 'http://www.mypeople.tw/index.php?r=site/json&first=1'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_json = json.loads(news_last_list_text)
        for i in text_json['news_new']:
            detail = dict()
            detail['url'] = i['data_link']
            news_last_list.append(detail)
        return news_last_list

    def crawling_news(self):
        try:
            self.get_cookie()
            news_last_list_text = self.get_news_last_list()
            news_last_list = self.analyze_news_last_list(news_last_list_text)
        except RequestError:
            print('list', RequestError)
        except AnalyzeError:
            print('list', AnalyzeError)
        else:
            total = 0
            for detail in news_last_list:
                try:
                    result_detail = self.auto_news_main_content(detail['url'])
                except RequestError:
                    print('cnt', RequestError)
                else:
                    self.result['result']['item'] = result_detail
                    try:
                        send(self.result)
                        # print(self.result)
                        time.sleep(0.1)
                        total += 1
                        if total >= 10:
                            break
                    except Exception:
                        print('send errors')

    # search
    @request_check
    def get_search_result(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        head['Cookie'] = self.cookie
        wb_url = 'http://www.mypeople.tw/?q={}'.format(str(self.req_params['keyword']))
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_search_result(self, search_result_text):
        news_last_list = list()
        text_tree = etree.HTML(search_result_text)
        trs = text_tree.xpath('//*[@id="newslist"]/li')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('article/div/div[1]/a/@href') or '')
            if href_url == '':
                continue
            if 'http' in href_url:
                detail['url'] = href_url
            else:
                detail['url'] = self.source_url + href_url
            news_last_list.append(detail)
        return news_last_list

    def crawling_search(self):
        try:
            self.get_cookie()
            search_result_text = self.get_search_result()
            search_result_list = self.analyze_search_result(search_result_text)
        except RequestError:
            print('list', RequestError)
        except AnalyzeError:
            print('list', AnalyzeError)
        else:
            total = 0
            for detail in search_result_list:
                try:
                    result_detail = self.auto_news_main_content(detail['url'],keyword=self.req_params['keyword'])
                except RequestError:
                    print('cnt', RequestError)
                else:
                    self.result['result']['item'] = result_detail
                    try:
                        send(self.result)
                        # print(self.result)
                        time.sleep(0.1)
                        total += 1
                        if total >= 100:
                            break
                    except Exception:
                        print('send errors')

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080",
#     "method": "search",
#     "keyword":"2020"
# }
# spid = MppSpider(req_params=req)
# spid.crawling_search()
