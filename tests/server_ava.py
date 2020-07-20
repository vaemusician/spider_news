import time
import base64
import json
import sys
import os

from flask import Flask, request, jsonify


def log(*args, **kw):
    print(time.time(), *args, **kw)
    sys.stdout.flush()


app = Flask(__name__)


@app.route('/')
def index():
    return 'index'


@app.route('/<path:p>')
def path(p):
    log('path', p)
    return p


@app.route('/test', methods=['GET', 'POST'])
def index_test():
    if request.method == 'GET':
        return {
            'test': 'test',
        }
    else:
        j = request.get_json(force=True)
        log('test', j)
        return jsonify(j)


tasks = []
channels = {}
result_tasks = []
messages = {}


def cache_message(s):
    path = 'msg.txt'
    with open(path, 'a+', encoding='utf-8') as f:
        f.write(s.decode('utf-8'))
        f.write('\n')


@app.route('/task/<task_id>', methods=['GET', 'POST'])
def task(task_id):
    if request.method == 'GET':
        channel_key = task_id + '.' + request.args.get('channel', '')
        if channel_key not in channels:
            channels[channel_key] = []

        channel = channels[channel_key]
        tasks = channel

        if len(tasks) > 0:
            t = tasks.pop()
            return jsonify(t)
        else:
            time.sleep(5)
            d = dict(
                task_id=task_id,
                code=204,
            )
            return jsonify(d)
    else:
        log(f'task {task_id} send msg', request.data)
        cache_message(request.data)
        j = json.loads(request.data)
        if task_id not in messages:
            messages[task_id] = []
        messages[task_id].append(j)
        return task_id


@app.route('/api/v2/task/<task_id>/message', methods=['POST'])
def send_msg(task_id):
    channel_key = task_id + '.' + request.args.get('channel', '')
    if channel_key not in channels:
        channels[channel_key] = []

    channel = channels[channel_key]
    tasks = channel

    task = json.loads(request.data)
    tasks.append(task)
    log('new task', channel_key, task)
    r = dict(
        msg=':)',
        data=dict(
            host_id='local',
        ),
    )
    return jsonify(r)


@app.route('/api/v2/task/<task_id>/messages', methods=['GET'])
def msgs(task_id):
    msgs = []
    last = request.args.get('last', type=int, default=-1)
    if task_id not in messages:
        messages[task_id] = []
    for i, task in enumerate(messages[task_id]):
        if i <= last:
            continue
        bs = json.dumps(task, ensure_ascii=False).encode('utf-8')
        b64 = base64.b64encode(bs)
        d = dict(
            data=dict(
                Data=b64,
            ),
            _id=i,
        )
        msgs.append(d)
    data = dict(
        data=msgs,
    )
    return jsonify(data)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5946,
        debug=False,
        threaded=True,
    )
