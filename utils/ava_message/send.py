import os
import socket
import struct
import json

import requests

from utils import log


class AVAMessageSender(object):

    def __init__(self):
        self.gateway = self.get_default_gateway_linux()
        # self.gateway = '127.0.0.1'
        self.port = 5946
        self.task_id = self.current_task_id() or 'local'
        self.url = f'http://{self.gateway}:{self.port}/task/{self.task_id}'

    @staticmethod
    def get_default_gateway_linux():
        if not os.path.exists('/proc/net/route'):
            return '127.0.0.1'

        """Read the default gateway directly from /proc."""
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    @staticmethod
    def current_task_id():
        k = 'TaskID'
        id_ = os.environ.get(k)
        return id_

    def send(self, message):
        if isinstance(message, dict):
            message = json.dumps(message, ensure_ascii=False)
        bs = message.encode('utf-8')
        r = requests.post(self.url, bs)
        log(f'Send ava message {message}')
        return r

    def __call__(self, message):
        return self.send(message)


send_message = AVAMessageSender()
