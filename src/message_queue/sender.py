import threading
from queue import Queue

from flask import render_template

from .message import Message


class Sender:
    def __init__(self, sender_id: str):
        self.sender_id = sender_id
        self.queue = Queue()
        self._stop_event = threading.Event()

    def send_message(self, msg_type, msg):
        search_result_step_html = render_template('search_result_step.html', search_result_step_json=[{'msg': msg}])
        self.queue.put(Message(sender_id=self.sender_id, msg_type=msg_type, msg={'msg': msg, 'html': search_result_step_html}))

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
