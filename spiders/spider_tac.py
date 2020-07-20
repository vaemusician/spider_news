import json
import re
import time
from hashlib import md5

import requests
from dateutil.parser import parse
from goose3 import Goose, Configuration
from goose3.text import StopWordsChinese

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y 苹果日报
class TacSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'tw.news.appledaily.com'
        self.source_url = 'https://tw.appledaily.com/'

    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        wb_url = 'https://tw.appledaily.com/pf/api/v3/content/fetch/query-feed?query=%7B%22feedOffset%22%3A0%2C%22feedQuery%22%3A%22type%253Astory%2520AND%2520taxonomy.primary_section._id%253A%252F%255C%252Frealtime.*%252F%22%2C%22feedSize%22%3A%22100%22%2C%22sort%22%3A%22display_date%3Adesc%22%7D&d=97&_website=tw-appledaily'

        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = json.loads(news_last_list_text)
        trs = text_tree['content_elements']
        for tr in trs:
            detail = dict()
            href_url = str(tr['website_url'] or '')
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
        head = dict()
        head[
            'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        req = requests.get(news_url, proxies=proxy, headers=head)
        cnt = ''.join(re.findall(r'content":"(.*?)"}', req.text, re.S) or '').replace('<br>', '').replace('\xa0',
                                                                                                          '').replace(
            '<br />', '').replace('&nbsp;', '').replace('</strong>', '').replace('<strong>', '').replace('<u>',
                                                                                                         '').replace(
            '</u>', '')
        if '<iframe' in cnt:
            cnt = ''.join(re.findall(r'(.*?)<iframe', cnt, re.S) or '')
        if '<div' in cnt:
            cnt = ''.join(re.findall(r'(.*?)<div', cnt, re.S)[0] or '')
        if 'allow=' in cnt:
            cnt = ''.join(re.findall(r'(.*?)allow=', cnt, re.S)[0] or '')
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
            content=cnt,
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

# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.63:1090"
# }
# spid = TacSpider(req_params=req)
# spid.crawling_news()
