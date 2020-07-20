import time

import requests
from lxml import etree
import json
from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y 香港大学电子邮件服务器(香港)
class HkuSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'Hkuportal.hku.hk'
        self.source_url = 'https://hku.hk/'

    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        # 本月所有新闻
        wb_url = 'https://hku.hk/press/all/c_index.html'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//div[@class="press-item"]')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('span[2]/a/@href') or '')
            if href_url == '':
                continue
            if 'http' in href_url:
                detail['url'] = href_url
            else:
                detail['url'] = self.source_url + href_url
            news_last_list.append(detail)
        return news_last_list


    def crawling_news(self):
        try:
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
                        if total >= 100:
                            break
                    except Exception:
                        print('send errors')

    # search
    @request_check
    def get_search_result(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://cse.google.com/cse/element/v1'
        params = (
            ('rsz', 'filtered_cse'),
            ('num', '20'),  # 数量
            ('hl', 'en'),
            ('source', 'gcsc'),
            ('gss', '.com'),
            ('cselibv', '26b8d00a7c7a0812'),
            ('cx', '004484284548649879936:lcyfpggwj-i'),
            ('q', self.req_params['keyword']),
            ('safe', 'off'),
            ('cse_tok', 'AJvRUv3ca232rlDz-TULCnxNtHRp:1594196725229'),  #
            ('exp', 'csqr,cc'),
            ('oq', self.req_params['keyword']),
            ('gs_l',
             'partner-generic.12...0.0.0.3377.0.0.0.0.0.0.0.0..0.0.csems,nrl=13...0.0....34.partner-generic..0.0.0.'),
            ('callback', 'google.search.cse.api16271'),
        )
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False, params=params)
        wb_res.encoding = 'utf-8'
        wb_json = ''.join(str(wb_res.text).split('(')[1:])[:-2]
        return wb_json

    @analyze_check
    def analyze_search_result(self, search_result_text):
        news_last_list = list()
        text_tree = json.loads(search_result_text)
        for result in text_tree['results']:
            detail = dict()
            detail['url'] = result['unescapedUrl']
            news_last_list.append(detail)
        return news_last_list

    def crawling_search(self):
        try:
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
                    result_detail = self.auto_news_main_content(detail['url'], keyword=self.req_params['keyword'])
                except RequestError:
                    print('cnt', RequestError)
                else:
                    self.result['result']['item'] = result_detail
                    try:
                        send(self.result)
                        # print(self.result)
                        time.sleep(0.1)
                        total += 1
                        if total >= 20:
                            break
                    except Exception:
                        print('send errors')

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080",
#     'method':'search',
#     "keyword":"中国"
# }
# spid = HkuSpider(req_params=req)
# spid.crawling_search()
