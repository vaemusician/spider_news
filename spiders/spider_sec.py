import time

import requests
from lxml import etree

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y  三立电视
class SecSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'www.setn.com'
        self.source_url = 'https://www.setn.com'

    # 即时
    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://www.setn.com/ViewAll.aspx'  # 每页42按时间排序
        proxy = {'http': self.proxy,
                 'https': self.proxy
                 }
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//div[@class="col-sm-12"]')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div/h3/a/@href') or '')
            if href_url == '':
                continue
            if 'http' in href_url:
                detail['url'] = href_url
            else:
                detail['url'] = self.source_url + href_url
            news_last_list.append(detail)
        return news_last_list

    # 热门
    @request_check
    def get_news_last_list_hot(self):
        head = dict()
        head[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        wb_url = 'https://www.setn.com/ViewAll.aspx?PageGroupID=0'  # 每页42按时间排序
        proxy = {'http': self.proxy,
                 'https': self.proxy
                 }
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list_hot(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//div[@class="col-sm-12"]')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div/h3/a/@href') or '')
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
            news_last_list_text_hot = self.get_news_last_list_hot()
            news_last_list_hot = self.analyze_news_last_list_hot(news_last_list_text_hot)
            news_list = news_last_list + news_last_list_hot
        except RequestError:
            print('list', RequestError)
        except AnalyzeError:
            print('list', AnalyzeError)
        else:
            total = 0
            for detail in news_list:
                try:
                    result_detail = self.auto_news_main_content(detail['url'])
                except RequestError:
                    print('cnt', RequestError)
                else:
                    self.result['result']['item'] = result_detail
                    try:
                        send(self.result)
                        time.sleep(0.1)
                        total += 1
                        if total >= 20:
                            break
                        # print(self.result)
                    except Exception:
                        print('send errors')

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080"
# }
# spid = SecSpider(req_params=req)
# spid.crawling_news()
