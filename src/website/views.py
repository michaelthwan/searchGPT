import os
import random
import string
import tracemalloc

import psutil
from flask import Blueprint, render_template, request

from SearchGPTService import SearchGPTService
from FrontendService import FrontendService
from Util import setup_logger
from website.sender import exporting_progress, Sender

logger = setup_logger('Views')
views = Blueprint('views', __name__)

process = psutil.Process(os.getpid())
tracemalloc.start()
memory_snapshot = None


@views.route('/', methods=['GET'])
@views.route('/index', methods=['GET'])
def start_page():
    request_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

    data_json = {'response_json': [], 'source_json': [], 'response_explain_json': [], 'source_explain_json': [],
                 'prompt_examples_json': FrontendService.get_prompt_examples_json()}
    return render_template("index.html",
                           search_text='' or "Please search for something.",
                           response_json=data_json.get('response_json'),
                           source_json=data_json.get('source_json'),
                           response_explain_json=data_json.get('response_explain_json'),
                           source_explain_json=data_json.get('source_explain_json'),
                           prompt_examples_json=data_json.get('prompt_examples_json'),
                           request_id=request_id, status="init",
                           error=None
                           )


@views.route('/search', methods=['POST'])
def index_page():
    error = None
    data_json = {'response_json': [], 'source_json': []}
    request_id = request.values.get('request_id')
    search_text = request.values.get('q')

    try:
        ui_overriden_config = {
            'bing_search_subscription_key': request.values.get('bing_search_subscription_key'),
            'openai_api_key': request.values.get('openai_api_key'),
            'is_use_source': request.values.get('is_use_source'),
            'llm_service_provider': request.values.get('llm_service_provider'),
            'llm_model': request.values.get('llm_model'),
            'language': request.values.get('language'),
        }
        logger.info(f"GET ui_overriden_config: {ui_overriden_config}")

        if search_text is not None:
            sender = Sender(request_id) if request_id is not None and request_id != "" else None
            search_gpt_service = SearchGPTService(ui_overriden_config, sender)
            _, _, data_json = search_gpt_service.query_and_get_answer(search_text=search_text)
    except Exception as e:
        error = str(e)

    if error is None:
        id = 'search-results'
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
        request_id_status_html = render_template('request_id_status_html.html', request_id=request_id, status="done")
    else:
        id = 'alert-box'
        result_html = render_template('alert_box.html', error=error)
        explain_html = render_template('explain_result.html',
                                       search_text=search_text,
                                       response_explain_json=[],
                                       source_explain_json=[],
                                       )
        request_id_status_html = render_template('request_id_status_html.html', request_id=request_id, status="error")
    return {
        'id': id,
        'html': result_html,
        'explain_html': explain_html,
        'request_id_status_html': request_id_status_html,
    }


@views.route('/progress')
def progress():
    request_id = request.values.get('request_id')
    request_dict = exporting_progress.get(request_id, '')
    return request_dict


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
