import traceback

from utils import log
from utils.ava_message import send, subscribe
from utils.ava_proxy import forward_proxy, release_proxy


class GlobalData:
    proxy_channel_count = 1


def async_request(channel, method, callback, **params):
    msg = dict(
        msg_type='request',
        channel=channel,
        method=method,
        params=params,
    )
    send(msg)
    subscribe(channel, callback)


def get_proxy_callback_warp(callback):
    def f(msg):
        proxy = msg.get('data')
        p = forward_proxy(proxy)
        try:
            callback(p)
        except Exception as e:
            s = traceback.format_exc()
            log('get proxy callback error', e, proxy, s)
        release_proxy(proxy)
    return f


def get_proxy_async(callback, **params):
    channel = 'proxy_' + GlobalData.proxy_channel_count.__str__()
    GlobalData.proxy_channel_count += 1
    method = 'get_proxy'
    f = get_proxy_callback_warp(callback)
    async_request(channel, method, f, **params)
