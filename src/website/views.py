import tracemalloc

import os
import psutil
from flask import Blueprint, render_template, request

from SearchGPTService import SearchGPTService
from Util import setup_logger

logger = setup_logger('Views')
views = Blueprint('views', __name__)


process = psutil.Process(os.getpid())
tracemalloc.start()
memory_snapshot = None


@views.route('/', methods=['GET'])
@views.route('/index', methods=['GET'])
def start_page():
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
            search_gpt_service = SearchGPTService(ui_overriden_config)
            _, _, data_json = search_gpt_service.query_and_get_answer(search_text=search_text)
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