import random
import string
import time
import tracemalloc

import os
import psutil
from flask import Blueprint, render_template, request, session
from flask_socketio import join_room, leave_room

from SearchGPTService import SearchGPTService
from Util import setup_logger
from app_context import AppContext
from message_queue.receiver import Receiver
from message_queue.sender import Sender

logger = setup_logger('Views')
views = Blueprint('views', __name__)
socketio = AppContext.socket_io

process = psutil.Process(os.getpid())
tracemalloc.start()
memory_snapshot = None


@socketio.on('connect')
def on_connect():
    join_room(session['session_id'])


@socketio.on('disconnect')
def on_connect():
    leave_room(session['session_id'])


@views.route('/', methods=['GET'])
@views.route('/index', methods=['GET'])
def start_page():
    if 'session_id' not in session:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(16))
        session['session_id'] = random_string

    data_json = {'response_json': [], 'source_json': [], 'response_explain_json': [], 'source_explain_json': []}
    return render_template("index.html",
                           search_text='' or "Please search for something.",
                           response_json=data_json.get('response_json'),
                           source_json=data_json.get('source_json'),
                           response_explain_json=data_json.get('response_explain_json'),
                           source_explain_json=data_json.get('source_explain_json'),
                           error=None
                           )


@views.route('/search', methods=['POST'])
def index_page():
    error = None
    data_json = {'response_json': [], 'source_json': []}
    search_text = request.values.get('q')

    try:
        ui_overriden_config = {
            'bing_search_subscription_key': request.values.get('bing_search_subscription_key'),
            'openai_api_key': request.values.get('openai_api_key'),
            'is_use_source': request.values.get('is_use_source'),
            'llm_service_provider': request.values.get('llm_service_provider'),
            'llm_model': request.values.get('llm_model'),
        }
        logger.info(f"GET ui_overriden_config: {ui_overriden_config}")

        if search_text is not None:
            sender = Sender(sender_id=session['session_id'])
            receiver = Receiver(sender)

            search_gpt_service = SearchGPTService(ui_overriden_config, sender=sender)
            _, _, data_json = search_gpt_service.query_and_get_answer(search_text=search_text)

            receiver.stop()

    except Exception as e:
        error = str(e)

    if error is None:
        result_html = render_template('search_result.html',
                                      search_text=search_text,
                                      response_json=data_json.get('response_json'),
                                      source_json=data_json.get('source_json'),
                                      )
        explain_html = render_template('explain_result.html',
                                       search_text=search_text,
                                       response_explain_json=data_json.get('response_explain_json'),
                                       source_explain_json=data_json.get('source_explain_json'),
                                       )

        return {
            'id': 'search-results',
            'html': result_html,
            'explain_html': explain_html,
        }
    else:
        result_html = render_template('alert_box.html', error=error)
        explain_html = render_template('explain_result.html',
                                       search_text=search_text,
                                       response_explain_json=[],
                                       source_explain_json=[],
                                       )
        return {
            'id': 'alert-box',
            'html': result_html,
            'explain_html': explain_html,
        }


@views.route('/test-socket', methods=['POST'])
def test_socket_io():
    time.sleep(1)
    socket_io = AppContext.socket_io
    for i in range(10):
        socket_io.emit('progress', i)
    return "OK"


@views.route('/index_static', methods=['GET', 'POST'])
def index_static_page():
    return render_template("index_static.html")


@views.route("/data", methods=["GET"])
def get_data():
    return {'id': 1, 'test': 'test'}


@views.route('/memory')
def print_memory():
    return {'memory': process.memory_info().rss}


@views.route("/snapshot")
def snap():
    global memory_snapshot
    if not memory_snapshot:
        memory_snapshot = tracemalloc.take_snapshot()
        return "taken snapshot\n"
    else:
        lines = []
        memory_snapshot_temp = tracemalloc.take_snapshot()
        top_stats = memory_snapshot_temp.compare_to(memory_snapshot, 'lineno')
        memory_snapshot = memory_snapshot_temp
        for stat in top_stats[:5]:
            lines.append(str(stat))
        return "\n".join(lines)
