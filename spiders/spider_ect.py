import time
from hashlib import md5

import requests
from dateutil.parser import parse
from goose3 import Goose, Configuration
from goose3.text import StopWordsChinese
from lxml import etree

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y  大纪元时报台湾版
class EctSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'www.epochtimes.com.tw'
        self.source_url = 'https://www.epochtimes.com.tw/'

    # 即时
    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        wb_url = 'https://www.epochtimes.com.tw/%E6%9C%80%E6%96%B0%E6%96%87%E7%AB%A0/all/%E5%85%A8%E9%83%A8/p/1'
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
        trs = text_tree.xpath('//*[@id="uid_relate_article"]/div/div')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div/div/a/@href') or '')
            if href_url == '':
                continue
            detail['url'] = self.source_url + href_url
            news_last_list.append(detail)
        return news_last_list

    @request_check
    def get_news_result_cnt(self, news_url):
        config = Configuration()
        config.http_proxies = {
            'http': self.proxy,
            'https': self.proxy
        }
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        config.stopwords_class = StopWordsChinese
        config.http_proxies = {
            'http': self.proxy,
            'https': self.proxy
        }
        g = Goose(config)
        article = g.extract(news_url)
        try:
            published_time = int(parse(article.publish_date).timestamp() * 1000) if article.publish_date else None
        except:
            published_time = int(
                time.mktime(time.strptime(article.publish_date, "%Y年%m月%d日")) * 1000) if article.publish_date else None
        news_post = dict(
            doc_id=md5(article.final_url.encode('utf-8')).hexdigest(),
            keyword='',
            url=article.final_url,
            title=article.title,
            platform='news',
            content=article.cleaned_text,
            author=article.authors,
            source=self.source,
            published_time=published_time,
            spi_time=int(time.time() * 1000)
        )
        return news_post

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
                    result_detail = self.get_news_result_cnt(detail['url'])
                except RequestError:
                    print('cnt', RequestError)
                else:
                    self.result['result']['item'] = result_detail
                    try:
                        send(self.result)
                        # print(self.result)
                        time.sleep(0.1)
                        total += 1
                        if total >= 50:
                            break
                    except Exception:
                        print('send errors')

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080"
# }
# spid = EctSpider(req_params=req)
# spid.crawling_news()
