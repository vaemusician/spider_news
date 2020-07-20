import json
import time

import requests

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y  自由时报
class NlctSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'news.ltn.com.tw'
        self.source_url = 'https://www.ltn.com.tw'

    # 即时
    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://news.ltn.com.tw/ajax/breakingnews/all/1'  # 每页20
        proxy = {'http': self.proxy,
                 'https': self.proxy
                 }
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = json.loads(news_last_list_text)
        data = text_tree['data']
        for d in data:
            detail = dict()
            detail['url'] = d['url']
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
                        if total >= 20:
                            break
                    except Exception:
                        print('send errors')

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080"
# }
# spid = NlctSpider(req_params=req)
# spid.crawling_news()
