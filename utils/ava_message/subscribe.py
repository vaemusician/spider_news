import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

import requests

from utils import log


class AVAMessageSubscriber(object):
    default_channel = ''

    def __init__(self, sender, max_channels=16):
        self.sender = sender
        self.workers = {}
        self.pulling_channels = set()
        self.message_queue = Queue(maxsize=max_channels)
        self.executor = ThreadPoolExecutor(max_workers=max_channels)

    def channel_url(self, channel):
        if channel == self.default_channel:
            url = self.sender.url
            return url
        else:
            url = self.sender.url + '?channel=' + channel
            return url

    def subscribe(self, channel, method):
        self.workers[channel] = method
        log('subscribed', channel, method.__name__)

    def unsubscribe(self, channel, method):
        self.workers.pop(channel, None)
        log('unsubscribed', channel, method.__name__)

    def __call__(self, channel, method):
        return self.subscribe(channel, method)

    def consume_messages(self) -> int:
        r = 0
        q = self.message_queue
        while not q.empty():
            channel, msg = q.get()
            if msg.get('code') != 204:
                r += 1
                method = self.workers[channel]
                try:
                    method(msg)
                except Exception as e:
                    s = traceback.format_exc()
                    log(f'worker run error', e, method.__name__, msg, s)
        return r

    def pull_message(self, channel):
        try:
            url = self.channel_url(channel)
            r = requests.get(url)
            msg = r.json()
            item = (channel, msg)
            self.message_queue.put(item)
        except Exception as e:
            s = traceback.format_exc()
            log(f'pull message error', e, channel, s)
        self.pulling_channels.remove(channel)

    def pull_idle_channels(self) -> int:
        # 拷贝建，防止执行过程中动态订阅添加键
        channels = list(self.workers.keys())
        r = 0
        for channel in channels:
            if channel not in self.pulling_channels:
                self.pulling_channels.add(channel)
                self.executor.submit(self.pull_message, channel)
                r += 1
        return r

    def run_loop(self):
        log('workers start watch')
        data = dict(
            msg_type='worker_start',
            time=time.time(),
        )
        self.sender(data)

        while True:
            try:
                m = self.consume_messages()
                n = self.pull_idle_channels()
                if m == 0 and n == 0:
                    time.sleep(1)
            except Exception as e:
                s = traceback.format_exc()
                log(f'subscriber loop error: {e}\n{s}')
                time.sleep(5)

    def run_loop_single_thread(self):
        log('workers start watch')
        data = dict(
            msg_type='worker_start',
            time=time.time(),
        )
        self.sender(data)

        while True:
            # 拷贝建，防止执行过程中动态订阅添加键
            channels = list(self.workers.keys())
            for channel in channels:
                try:
                    url = self.channel_url(channel)
                    r = requests.get(url)
                    msg = r.json()
                    if msg.get('code') != 204:
                        method = self.workers[channel]
                        method(msg)
                except Exception as e:
                    s = traceback.format_exc()
                    log(f'worker run error: {e}\n{s}')
                    time.sleep(5)
