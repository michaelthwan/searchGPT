import threading
from queue import Queue

from .message import Message


class Sender:
    def __init__(self):
        self.queue = Queue()
        self._stop_event = threading.Event()

    def send_message(self, message: Message):
        self.queue.put(message)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
