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


# Y 共同民主党（韩国）
class MjooSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'https://theminjoo.kr'
        self.source_url = 'https://theminjoo.kr'

    @request_check
    def get_news_last_list(self,page=1):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://theminjoo.kr/board/lists/briefing?page={}'.format(str(page))
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//*[@id="boardPostList"]/li')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div[2]/a/@href') or '')
            if href_url == '':
                continue
            if 'http' in href_url:
                detail['url'] = href_url
            else:
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
            cont = ''.join(text_tree.xpath('//*[@id="content"]/div[2]//text()')).replace(' ','')
        if article.title == '더불어민주당':
            art_title = ''.join(text_tree.xpath('//*[@id="content"]/div[1]/h2/text()'))
        else:
            art_title = article.title
        news_post = dict(
            doc_id=md5(article.final_url.encode('utf-8')).hexdigest(),
            keyword='',
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
            current_page = 1
            news_last_list_all = list()
            for _ in range(5):
                news_last_list_text = self.get_news_last_list(current_page)
                news_last_list = self.analyze_news_last_list(news_last_list_text)
                news_last_list_all.extend(news_last_list)
                current_page += 1
        except RequestError:
            print('list', RequestError)
        except AnalyzeError:
            print('list', AnalyzeError)
        else:
            total = 0
            for detail in news_last_list_all:
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


# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080"
# }
# spid = MjooSpider(req_params=req)
# spid.crawling_news()
