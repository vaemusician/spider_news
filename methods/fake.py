import time

import requests

from utils.ava_message import send_message as send


def echo(**kw):
    return kw



def delay_echo(**kw):
    t = kw.get('sleep', 0)
    time.sleep(t)
    return kw


def ip(**kw):
    t = kw.get('sleep', 0)
    time.sleep(t)
    proxy = kw.get('proxy')
    url = 'http://ifconfig.me/ip'
    proxies = {
        'all': proxy,
    }
    r = requests.get(url, proxies=proxies)
    return r.text


def pick(**kw):
    msg = kw.get('task_msg')
    for i in range(5):
        data = dict(
            msg_type='scraped_data',
            result=dict(
                a=i,
            ),
            task_msg=msg,
        )
        send(data)
