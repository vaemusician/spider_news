import json

import requests

from utils import log


debug = False


def proxy_by_message(msg):
    proxy = msg.get('params').get('proxy')
    r = forward_proxy(proxy)
    return r


def forward_proxy(proxy):
    if debug or proxy is None:
        return proxy

    url = 'http://bastion/forward'
    if isinstance(proxy, dict):
        data = proxy
    else:
        data = json.dumps(proxy)
    r = requests.post(url, json=data)
    proxy = r.text
    log('use local forward proxy', proxy)
    return proxy


def release_proxy(proxy):
    if debug or proxy is None:
        return

    url = 'http://bastion/release'
    if isinstance(proxy, dict):
        data = proxy
    else:
        data = json.dumps(proxy)
    r = requests.post(url, json=data)
    log('release proxy', proxy, r.status_code, r.text)
