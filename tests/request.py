import requests

from utils import log


def test_fake_echo():
    p = dict(
        method='fake.echo',
        params=dict(
            a=1,
            proxy='',
        ),
    )
    # deal_message(p)
    ava_base_url = 'http://localhost:5946'
    ava_task_id = 'local'
    url = f"{ava_base_url}/api/v2/task/{ava_task_id}/message"
    r = requests.post(url, json=p)
    log('test_fake_echo', r.status_code, r.text)


def test_fake_pick():
    p = dict(
        method='fake.pick',
        params=dict(
            a=1,
            proxy='',
        ),
    )
    # deal_message(p)
    ava_base_url = 'http://localhost:5946'
    ava_task_id = 'test'
    url = f"{ava_base_url}/api/v2/task/{ava_task_id}/message"
    r = requests.post(url, json=p)
    log('test_fake_echo', r.status_code, r.text)


def test_concurrent():
    for i in range(4):
        p = dict(
            method='fake.delay_echo',
            params=dict(
                i=i,
                sleep=1,
            ),
        )
        # deal_message(p)
        ava_base_url = 'http://172.16.102.84:10086'
        # ava_base_url = 'http://localhost:5946'
        ava_task_id = '5ee0575ac262ac34a27d1a18'
        # ava_task_id = 'local'
        url = f"{ava_base_url}/api/v2/task/{ava_task_id}/message"
        r = requests.post(url, json=p)
        log('test_concurrent', r.status_code, r.text)


def test_stop_task():
    p = dict(
        method='fake.delay_echo',
        params=dict(
            sleep=30,
        ),
        _id=1,
    )
    # deal_message(p)
    ava_base_url = 'http://172.16.102.84:10086'
    # ava_base_url = 'http://localhost:5946'
    ava_task_id = '5ee0575ac262ac34a27d1a18'
    # ava_task_id = 'local'
    url = f"{ava_base_url}/api/v2/task/{ava_task_id}/message"
    r = requests.post(url, json=p)
    log('test_stop_task', r.status_code, r.text)

    p = dict(
        command='stop',
        method='fake.delay_echo',
        _id=1,
    )
    url = url + '?channel=f_fake.delay_echo_1'
    requests.post(url, json=p)
