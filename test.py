from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Process, Pool
import time
import asyncio

import requests
import aiohttp

from utils import log
from utils.ava_message import send_message as send
from manager import TaskManager


def send_msg(msg):
    time.sleep(2)
    send(msg)


def __test_concurrent():
    log('main called')

    executor = ProcessPoolExecutor(max_workers=4)
    executor.submit(send_msg, dict(i=1))

    resp = requests.get(send.url)
    msg = resp.json()
    log('get msg 1', msg)

    executor.submit(send_msg, dict(i=2))

    resp = requests.get(send.url)
    msg = resp.json()
    log('get msg 2', msg)


executor = ProcessPoolExecutor(max_workers=2)


def tlog(s):
    log(s)
    time.sleep(5)
    log('log end')


async def aio_get(url):
    async with aiohttp.request('GET', url) as r:
        r = await r.text()
        executor.submit(tlog, r)


async def __test_aio():
    url = 'http://ifconfig.me/ip'
    await aio_get(url)


def __test_executor_cancel():
    r = executor.submit(tlog, 'test task')
    log(r, r.__dir__())
    time.sleep(1)
    # s = r.cancel()
    # s = r.set_exception('')
    s = r.close()
    log(s)
    as_completed([r])


def __test_process_cancel():
    p = Process(target=tlog, args=('test task',))
    p.start()
    # time.sleep(1)
    # p.terminate()
    # time.sleep(5)
    p.join()
    s = p.is_alive()
    log('__test_process_cancel end', s)


def __test_pool_cancel():
    tm = TaskManager()
    msg = dict(
        method='fake.delay_echo',
        params=dict(
            sleep=5,
        ),
    )
    tm.start_task_by_msg(msg)
    tm.wait_tasks()


def main():
    # loop = asyncio.get_event_loop()
    # r = loop.run_until_complete(__test_aio())

    # __test_process_cancel()
    __test_pool_cancel()


if __name__ == '__main__':
    main()
