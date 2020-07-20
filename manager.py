import traceback
import time
import importlib
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process

import requests

from utils import log
from utils.ava_message import send, subscribe, unsubscribe
from utils.ava_proxy import proxy_by_message, release_proxy


def method_and_params_by_message(msg):
    method_name = msg.get('method')
    module_name, f = method_name.split('.', 1)
    module = importlib.import_module(f'methods.{module_name}')
    method = getattr(module, f)
    params = msg.get('params', {})
    return method, params


def execute_by_message(message):
    msg = message
    method, params = method_and_params_by_message(msg)
    raw_proxy = params.get('proxy')
    params['proxy'] = proxy_by_message(msg)
    msg.pop('params', None)
    p = dict(
        task_msg=msg,
    )
    p.update(params)
    try:
        result = method(**p)
    except Exception as e:
        s = traceback.format_exc()
        log(f'execute task error: {msg}\n{e}\n{s}')
        result = dict(
            code=1899999,
            data=dict(
                error=str(e),
                detail=s,
            ),
            msg='爬虫未知错误',
        )
    release_proxy(raw_proxy)
    params['proxy'] = raw_proxy
    data = dict(
        msg_type='method_result',
        result=result,
        task_msg=msg,
    )
    send(data)


def deal_message(msg):
    try:
        log(f'dealing msg {msg}')
        execute_by_message(msg)
    except Exception as e:
        s = traceback.format_exc()
        log(f'deal msg error: {msg}\n{e}\n{s}')
        data = dict(
            msg_type='deal_msg_error',
            error_detail=s,
            task_msg=msg,
        )
        send(data)


class TaskManager(object):
    class Command:
        stop = 'stop'

    def __init__(self, max_workers=4):
        # TODO: max_workers
        self.max_workers = max_workers
        self.increment_id = 1
        self.tasks = {}

    def task_channel(self, method, _id):
        r = f'f_{method}_{_id}'
        return r

    def clear_done_tasks(self):
        done_channels = []
        for channel, p in self.tasks.items():
            p: Process
            if not p.is_alive():
                done_channels.append(channel)

        for channel in done_channels:
            self.tasks.pop(channel)
            unsubscribe(channel, self.deal_task_channel_msg)

    def start_task_by_msg(self, msg):
        _id = msg.get('_id')
        if _id is None:
            _id = self.increment_id
            self.increment_id += 1

        p = Process(target=deal_message, args=(msg,))
        p.start()
        method = msg.get('method')
        k = self.task_channel(method, _id)
        self.tasks[k] = p

        # subscribe channel
        channel = self.task_channel(method, _id)
        subscribe(channel, self.deal_task_channel_msg)

        # clear done task
        self.clear_done_tasks()

    def submit(self, method, msg):
        return self.start_task_by_msg(msg)

    def stop_task(self, method, _id):
        k = self.task_channel(method, _id)
        p: Process = self.tasks.pop(k)
        p.terminate()
        channel = self.task_channel(method, _id)
        log('stopped task', method, _id)
        unsubscribe(channel, self.deal_task_channel_msg)
        # TODO: process state judge

    def stop_task_by_msg(self, msg):
        method = msg.get('method')
        _id = msg.get('_id')
        self.stop_task(method, _id)

    def deal_task_channel_msg(self, msg):
        # log('dealing task channel msg', msg)
        command = msg.get('command')
        if command == self.Command.stop:
            self.stop_task_by_msg(msg)
        else:
            log('unexpected command', command, msg)

    def wait_tasks(self):
        for p in self.tasks.values():
            p.join()
