from .message import Message
from .post_msg_receive import post_msg_receive_search_step, post_msg_openai_stream

MSG_TYPE_SEARCH_STEP = 'search-step'
MSG_TYPE_OPEN_AI_STREAM = 'openai-stream'

post_msg_func_map = {
    MSG_TYPE_SEARCH_STEP: post_msg_receive_search_step,
    MSG_TYPE_OPEN_AI_STREAM: post_msg_openai_stream
}
