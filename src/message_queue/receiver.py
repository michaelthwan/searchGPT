import threading
from collections import defaultdict
from queue import Empty

from . import post_msg_func_map
from .message import Message
from .sender import Sender


class Receiver:
    def __init__(self, sender: Sender):
        self.sender: Sender = sender
        self.received_msgs = defaultdict(lambda: list())
        self.thread = threading.Thread(target=self._receive_messages)
        self.thread.start()

    def _receive_messages(self):
        while not self.sender.stopped():
            try:
                message: Message = self.sender.queue.get(timeout=1)
                self.received_msgs[message.msg_type].append(message.msg)
                post_msg_func_map[message.msg_type](msg=message, received_msgs=self.received_msgs[message.msg_type])
            except Empty:
                pass

    def stop(self):
        self.sender.stop()
        self.thread.join()
