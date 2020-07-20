import time
from concurrent.futures import ProcessPoolExecutor


log = print


def echo(msg):
    log('echo', msg)
    time.sleep(0.1)


def __test():
    executor = ProcessPoolExecutor(max_workers=2)
    for i in range(100):
        executor.submit(echo, i)
    log('test end')


if __name__ == '__main__':
    __test()
