import json
import time
from hashlib import md5

import requests
from dateutil.parser import parse
from goose3 import Goose, Configuration
from goose3.text import StopWordsChinese

from spiders.decorators import *
from spiders.spider import Spider
from utils.ava_message import send_message as send


# Y  战国策传播集团
class JetgoSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source = 'https://jetgo.com.tw/'
        self.source_url = 'https://jetgo.com.tw'

    @request_check
    def get_news_last_list(self, current_page=1):
        headers = {
            'authority': 'jetgo.com.tw',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept': '*/*',
            'origin': 'https://jetgo.com.tw',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://jetgo.com.tw/',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'PHPSESSID=d6f4ec5cc84c9bfbbd143f514142bea5; _ga=GA1.3.360536827.1593748734; _gid=GA1.3.804212879.1593748734',
        }

        params = (
            ('infinity', 'scrolling'),
        )

        data = {
            'action': 'infinite_scroll',
            'page': '{}'.format(str(current_page)),
            'currentday': '13.12.19',
            'order': 'DESC',
            'scripts[0]': 'jquery-core',
            'scripts[1]': 'jquery-migrate',
            'scripts[2]': 'jquery',
            'scripts[3]': 'spin',
            'scripts[4]': 'jquery.spin',
            'scripts[5]': 'tiled-gallery',
            'scripts[6]': 'the-neverending-homepage',
            'scripts[7]': 'jetpack-photon',
            'scripts[8]': 'jetpack-carousel',
            'scripts[9]': 'baskerville-2-skip-link-focus-fix',
            'scripts[10]': 'baskerville-2-flexslider',
            'scripts[11]': 'imagesloaded',
            'scripts[12]': 'masonry',
            'scripts[13]': 'baskerville-2-global',
            'scripts[14]': 'jetpack-facebook-embed',
            'scripts[15]': 'wp-embed',
            'scripts[16]': 'font-awesome-4-shim',
            'scripts[17]': 'elementor-frontend-modules',
            'scripts[18]': 'jquery-ui-position',
            'scripts[19]': 'elementor-dialog',
            'scripts[20]': 'elementor-waypoints',
            'scripts[21]': 'swiper',
            'scripts[22]': 'share-link',
            'scripts[23]': 'elementor-frontend',
            'scripts[24]': 'sharing-js',
            'styles[0]': 'the-neverending-homepage',
            'styles[1]': 'wp-block-library',
            'styles[2]': 'global-styles',
            'styles[3]': 'jetpack_likes',
            'styles[4]': 'jetpack-carousel',
            'styles[5]': 'tiled-gallery',
            'styles[6]': 'baskerville-2-style',
            'styles[7]': 'baskerville-2-fonts',
            'styles[8]': 'fontawesome',
            'styles[9]': 'baskerville-2-wpcom',
            'styles[10]': 'jetpack_facebook_likebox',
            'styles[11]': 'sharedaddy',
            'styles[12]': 'social-logos',
            'styles[13]': 'jetpack_css',
            'styles[14]': 'elementor-frontend',
            'styles[15]': 'elementor-post-2368',
            'styles[16]': 'elementor-post-2202',
            'styles[17]': 'elementor-post-2074',
            'styles[18]': 'elementor-post-1971',
            'styles[19]': 'elementor-icons',
            'styles[20]': 'elementor-animations',
            'styles[21]': 'font-awesome-5-all',
            'styles[22]': 'font-awesome-4-shim',
            'styles[23]': 'elementor-global',
            'styles[24]': 'google-fonts-1',
            'styles[25]': 'elementor-icons-shared-0',
            'styles[26]': 'elementor-icons-fa-solid',
            'query_args[error]': '',
            'query_args[m]': '',
            'query_args[p]': '0',
            'query_args[post_parent]': '',
            'query_args[subpost]': '',
            'query_args[subpost_id]': '',
            'query_args[attachment]': '',
            'query_args[attachment_id]': '0',
            'query_args[name]': '',
            'query_args[pagename]': '',
            'query_args[page_id]': '0',
            'query_args[second]': '',
            'query_args[minute]': '',
            'query_args[hour]': '',
            'query_args[day]': '0',
            'query_args[monthnum]': '0',
            'query_args[year]': '0',
            'query_args[w]': '0',
            'query_args[category_name]': '',
            'query_args[tag]': '',
            'query_args[cat]': '',
            'query_args[tag_id]': '',
            'query_args[author]': '',
            'query_args[author_name]': '',
            'query_args[feed]': '',
            'query_args[tb]': '',
            'query_args[paged]': '0',
            'query_args[meta_key]': '',
            'query_args[meta_value]': '',
            'query_args[preview]': '',
            'query_args[s]': '',
            'query_args[sentence]': '',
            'query_args[title]': '',
            'query_args[fields]': '',
            'query_args[menu_order]': '',
            'query_args[embed]': '',
            'query_args[category__in][]': '',
            'query_args[category__not_in][]': '',
            'query_args[category__and][]': '',
            'query_args[post__in][]': '',
            'query_args[post__not_in][]': '',
            'query_args[post_name__in][]': '',
            'query_args[tag__in][]': '',
            'query_args[tag__not_in][]': '',
            'query_args[tag__and][]': '',
            'query_args[tag_slug__in][]': '',
            'query_args[tag_slug__and][]': '',
            'query_args[post_parent__in][]': '',
            'query_args[post_parent__not_in][]': '',
            'query_args[author__in][]': '',
            'query_args[author__not_in][]': '',
            'query_args[posts_per_page]': '9',
            'query_args[ignore_sticky_posts]': 'false',
            'query_args[suppress_filters]': 'false',
            'query_args[cache_results]': 'false',
            'query_args[update_post_term_cache]': 'true',
            'query_args[lazy_load_term_meta]': 'true',
            'query_args[update_post_meta_cache]': 'true',
            'query_args[post_type]': '',
            'query_args[nopaging]': 'false',
            'query_args[comments_per_page]': '50',
            'query_args[no_found_rows]': 'false',
            'query_args[order]': 'DESC',
            'query_before': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'last_post_date': '2019-12-13 18:23:55'
        }

        wb_url = 'https://jetgo.com.tw/'  # 每页10(共5页)按时间排序
        proxy = {'http': self.proxy,
                 'https': self.proxy
                 }
        wb_res = requests.post(wb_url, headers=headers, params=params, data=data, proxies=proxy)
        wb_res.encoding = 'utf-8'
        return wb_res.text

    @analyze_check
    def analyze_news_last_list(self, news_last_list_text):
        news_last_list = list()
        text_json = json.loads(news_last_list_text)
        post_flair = text_json['postflair']
        for k, v in post_flair.items():
            detail = dict()
            detail['url'] = k
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
            current_page = 1
            news_last_list_all = list()
            for i in range(6):
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
                        if total >= 50:
                            break
                    except Exception:
                        print('send errors')

#
# req = {
#     "task_msg": "",
#     "proxy": "http://172.16.102.96:1080"
# }
# spid = JetgoSpider(req_params=req)
# spid.crawling_news()
