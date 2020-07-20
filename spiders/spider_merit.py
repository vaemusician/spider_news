import time

import requests
from lxml import etree

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y 人间福报（台湾）
class MeritSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'http://www.merit-times.com/'
        self.source_url = 'https://www.merit-times.com/'
        self.data = dict()

    @request_check
    def get_data(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://www.merit-times.com/search.aspx'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        tree_text = etree.HTML(wb_res.text)
        self.data['__EVENTTARGET'] = str(tree_text.xpath('//*[@id="__EVENTTARGET"]/@value')[0] or '')
        self.data['__EVENTARGUMENT'] = str(tree_text.xpath('//*[@id="__EVENTARGUMENT"]/@value')[0] or '')
        self.data['__VIEWSTATE'] = str(tree_text.xpath('//*[@id="__VIEWSTATE"]/@value')[0] or '')
        self.data['__VIEWSTATEGENERATOR'] = str(tree_text.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')[0] or '')
        self.data['__EVENTVALIDATION'] = str(tree_text.xpath('//*[@id="__EVENTVALIDATION"]/@value')[0] or '')

        self.data['UserControl_header$TextBox_\u641C\u5C0B'] = ''
        self.data['CheckBox_\u6A19\u984C'] = 'on'
        self.data['TextBox_\u95DC\u9375\u5B57'] = self.req_params['keyword']
        self.data['Button_\u641C\u5C0B'] = '\u9032\u968E\u641C\u5C0B'
        self.data['UserControl_email1$TextBox_\u8A02\u95B1\u96FB\u90F5'] = ''
        self.data['UserControl_footer$TextBox_\u96FB\u90F5\u5730\u5740'] = ''

    # news
    @request_check
    def get_news_last_list(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        # 今日新闻焦点
        wb_url = 'https://www.merit-times.com/PageList.aspx?classid=7'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.get(wb_url, headers=head, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_tree = etree.HTML(news_last_list_text)
        trs = text_tree.xpath('//*[@id="main"]/article/section[1]/div/div[1]/div')
        for tr in trs:
            detail = dict()
            href_url = ''.join(tr.xpath('div[2]/div[1]/a/@href') or '')
            if href_url == '':
                continue
            if 'http' in href_url:
                detail['url'] = href_url
            else:
                detail['url'] = self.source_url + href_url
            news_last_list.append(detail)
        trs_hot = text_tree.xpath('//*[@id="main"]/article/section[1]/div/div[3]/div[3]/ul/li')
        for tr in trs_hot:
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

    # search
    @request_check
    def get_search_result(self):
        head = dict()
        head[
            'User-Agent'] = self.ua
        wb_url = 'https://www.merit-times.com/search.aspx'
        proxy = {'http': self.proxy,
                 'https': self.proxy}
        wb_res = requests.post(wb_url, headers=head, data=self.data, proxies=proxy, verify=False)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_search_result(self, search_result_text):
        news_last_list = list()
        text_tree = etree.HTML(search_result_text)
        trs = text_tree.xpath('//div[@class="newsTxt flexBox"]')
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

    def crawling_search(self):
        try:
            self.get_data()
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
                    result_detail = self.auto_news_main_content(detail['url'], self.req_params['keyword'])
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
#     "keyword": "00"
# }
# spid = MeritSpider(req_params=req)
# spid.crawling_search()
