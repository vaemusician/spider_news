import json
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


# Y 外务省（日本）
class MofaSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'https://www.mofa.go.jp/'
        self.source_url = 'https://www.mofa.go.jp/'

    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://www.mofa.go.jp/mofaj/press/release/index.html'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//*[@id="pressrelease"]/dl/dd/ul/li')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('a/@href') or '')
            if href_url == '':
                continue
            if 'http' in href_url:
                detail['url'] = href_url
            else:
                detail['url'] = self.source_url + href_url
            news_last_list.append(detail)
        return news_last_list

    @request_check
    def get_news_result_cnt(self, news_url,keyword=''):
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
        if article.cleaned_text:
            cont = article.cleaned_text
        else:
            text_html = article.raw_html
            text_tree = etree.HTML(text_html)
            cont = ''.join(text_tree.xpath('//div[@class="text"]//text()')).replace(' ', '')
        news_post = dict(
            doc_id=md5(article.final_url.encode('utf-8')).hexdigest(),
            keyword=keyword,
            url=article.final_url,
            title=article.title,
            platform='news',
            content=cont,
            author=article.authors,
            source=self.source,
            published_time=int(parse(article.publish_date).timestamp() * 1000) if article.publish_date else None,
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
            ('hl', 'zh-CN'),
            ('source', 'gcsc'),
            ('gss', '.jp'),
            ('cselibv', '57975621473fd078'),
            ('cx', '011758268112499481406:fkqokg_sxzw'),
            ('q', self.req_params['keyword']),
            ('safe', 'off'),
            ('cse_tok', 'AJvRUv1aTjtoLAm32-psaOP47BeI:1594261215651'),  #
            ('exp', 'csqr,cc'),
            ('sort', ''),
            ('callback', 'google.search.cse.api5691'),
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
                    result_detail = self.get_news_result_cnt(detail['url'], keyword=self.req_params['keyword'])
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
#     'method':'search',
#     "keyword":"2020"
# }
# spid = MofaSpider(req_params=req)
# spid.crawling_search()
