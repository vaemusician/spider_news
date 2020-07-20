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


# Y 印尼《共和国报》（印）
class RciSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'https://www.republika.co.id/'
        self.source_url = 'https://www.republika.co.id/'

    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://republika.co.id/ajax/latest_news/100/0/news/load_more/news/'  # 100 page_size 0 index
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//div[@class="center_conten1"]')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div[2]/div[1]/h2/a/@href') or '')
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
        text_html = article.raw_html
        text_tree = etree.HTML(text_html)
        if article.cleaned_text:
            cont = article.cleaned_text
        else:
            cont = ''.join(text_tree.xpath('//div[@class="artikel"]/p//text()')).replace('\xa0', '').replace('  ', '')
        art_title = article.title
        news_post = dict(
            doc_id=md5(article.final_url.encode('utf-8')).hexdigest(),
            keyword=keyword,
            url=article.final_url,
            title=art_title,
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
        wb_url = 'https://republika.co.id/search/2020/'
        data = {
            "datestart": '',
            "dateend": "",
            "q": self.req_params['keyword'],
            "sort-type": "relevansi",
            'offset': "0"

        }
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.post(wb_url, headers=head,data=data, proxies=proxy, verify=False, )
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_search_result(self, search_result_text):
        news_last_list = list()
        text_tree = etree.HTML(search_result_text)
        trs = text_tree.xpath('//div[@class="set_subkanal item-cari"]')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div[2]/h2/a/@href') or '')
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
#     "method": "search",
#     "keyword": "2020"
# }
# spid = RciSpider(req_params=req)
# spid.crawling_search()
