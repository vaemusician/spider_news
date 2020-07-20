import sys
import time
import logging


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.ERROR)


def log(*args, **kw):
    time_style = '[%Y-%m-%d %H:%M:%S]'
    now = time.time()
    time_array = time.localtime(now)
    time_prefix = time.strftime(time_style, time_array)
    print(time_prefix, *args, **kw)
    sys.stdout.flush()
