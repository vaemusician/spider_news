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


# Y 台湾民主基金会
class TfotSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'www.tfd.org.tw'
        self.source_url = 'http://www.tfd.org.tw'

    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        head['Accept-Encoding'] = 'gzip, deflate'
        head['Accept-Language'] = 'zh-CN,zh;q=0.9'
        head[
            'Cookie'] = '__utmc=93059612; __utmz=93059612.1593575079.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=93059612.1911873373.1593575079.1593582584.1593584879.3; __utmb=93059612.4.10.1593584879'
        head['Host'] = 'www.pct.org.tw'
        head['Proxy-Connection'] = 'keep-alive'
        head['Referer'] = 'http://www.pct.org.tw/'
        head['Upgrade-Insecure-Requests'] = '1'
        head[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'

        wb_url = 'http://www.tfd.org.tw/opencms/chinese/events/recent.html'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//*[@id="content"]/div')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('h3/a/@href') or '')
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
        news_post = dict(
            doc_id=md5(article.final_url.encode('utf-8')).hexdigest(),
            keyword='',
            url=article.final_url,
            title=article.title,
            platform='news',
            content=article.cleaned_text,
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
                        if total >= 5:
                            break
                    except Exception:
                        print('send errors')

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.63:1090"
# }
# spid = CntSpider(req_params=req)
# spid.crawling_news()
