from app_context import AppContext
from message_queue import Message


def post_msg_receive_search_step(msg: Message):
    socket_io = AppContext.socket_io
    socket_io.emit(msg.msg_type, msg.msg)


def post_msg_openai_stream(msg: Message):
    pass
