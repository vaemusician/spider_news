import time

import requests
from lxml import etree

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y 中时电子报
class CtcSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'www.chinatimes.com'
        self.source_url = 'https://www.chinatimes.com'

    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://www.chinatimes.com/realtimenews/?chdtv'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('/html/body/div[2]/div/div[2]/div/section/ul/li')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div/div/div/h3/a/@href') or '')
            if href_url == '':
                continue
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
                        if total >= 30:
                            break
                    except Exception:
                        print('send errors')

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080"
# }
# spid = CtcSpider(req_params=req)
# spid.crawling_news()
