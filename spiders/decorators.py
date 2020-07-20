from spiders.spider_errors import *


def request_check(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raise RequestError()

    return inner


def analyze_check(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raise AnalyzeError()

    return inner
