from flask import render_template

from app_context import SearchGPTContext
from message_queue import Message


def post_msg_receive_search_step(msg: Message, **kwargs):
    received_step_events: list = kwargs['received_msgs']
    with SearchGPTContext.app.app_context():
        search_result_step_html = render_template('search_result_step.html', search_result_step_json=[{'msg': received_msg} for received_msg in received_step_events])

    socket_io = SearchGPTContext.socket_io
    socket_io.emit(msg.msg_type, {'msg': msg.msg, 'html': search_result_step_html}, room=msg.sender_id)


def post_msg_openai_stream(msg: Message, **kwargs):
    socket_io = SearchGPTContext.socket_io
    socket_io.emit(msg.msg_type, {'msg': msg.msg}, room=msg.sender_id)
