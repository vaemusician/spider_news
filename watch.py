import traceback
import time
import importlib
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

import requests

from utils import log
from utils.ava_message import send, subscribe
from utils.ava_proxy import proxy_by_message, release_proxy
from manager import TaskManager


def method_and_params_by_message(msg):
    method_name = msg.get('method')
    module_name, f = method_name.split('.', 1)
    module = importlib.import_module(f'methods.{module_name}')
    method = getattr(module, f)
    params = msg.get('params')
    return method, params


def execute_by_message(message):
    msg = message
    method, params = method_and_params_by_message(msg)
    raw_proxy = params.get('proxy')
    params['proxy'] = proxy_by_message(msg)
    p = dict(
        task_msg=msg,
    )
    p.update(params)
    result = method(**p)
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


def __watch(thread_pool_executor=None):
    executor = thread_pool_executor
    log('Worker start watch channel test_01')
    data = dict(
        msg_type='worker_start',
        time=time.time(),
    )
    send(data)

    while True:
        try:
            url = send.url + '?channel=test_01'
            resp = requests.get(url)
            msg = resp.json()
            if msg.get('code') != 204:
                if executor is None:
                    deal_message(msg)
                else:
                    executor.submit(deal_message, msg)
        except Exception as e:
            s = traceback.format_exc()
            log(f'Unexpected error: {e}\n{s}')
            time.sleep(5)


def watch(task_manager=None):
    log('worker start watch')
    data = dict(
        msg_type='worker_start',
        time=time.time(),
    )
    send(data)

    while True:
        try:
            url = send.url
            resp = requests.get(url)
            msg = resp.json()
            if msg.get('code') != 204:
                if task_manager is None:
                    deal_message(msg)
                else:
                    task_manager.submit(deal_message, msg)
        except Exception as e:
            s = traceback.format_exc()
            log(f'Unexpected error: {e}\n{s}')
            time.sleep(5)


def main():
    executor = TaskManager(max_workers=4)
    subscribe(subscribe.default_channel, executor.start_task_by_msg)
    subscribe.run_loop()


if __name__ == '__main__':
    # executor = None
    # executor = ThreadPoolExecutor(max_workers=4)
    # executor = ProcessPoolExecutor(max_workers=4)
    # executor = TaskManager(max_workers=4)
    # watch(executor)
    main()
