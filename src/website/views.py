from flask import Blueprint, render_template, request
from SearchGPTService import SearchGPTService
from Util import setup_logger

logger = setup_logger('Views')
views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@views.route('/index', methods=['GET'])
def index_page():
    error = None
    try:
        search_text = request.values.get('q')
        ui_overriden_config = {
            'bing_search_subscription_key': request.values.get('bing_search_subscription_key'),
            'openai_api_key': request.values.get('openai_api_key'),
            'is_use_source': request.values.get('is_use_source'),
            'llm_service_provider': request.values.get('llm_service_provider'),
            'llm_model': request.values.get('llm_model'),
            'semantic_search_provider': request.values.get('semantic_search_provider'),
        }
        logger.info(f"GET ui_overriden_config: {ui_overriden_config}")

        data_json = {'response_json': [], 'source_json': []}
        if search_text is not None:
            search_gpt_service = SearchGPTService(ui_overriden_config)
            response_text, response_text_with_footnote, source_text, data_json = search_gpt_service.query_and_get_answer(search_text)
            # response_text, response_text_with_footnote, source_text, data_json = "test", "test", "test", {'response_json': [], 'source_json': []}
    except Exception as e:
        error = str(e)
    return render_template("index.html",
                           search_text=search_text or "Please search for something.",
                           response_json=data_json.get('response_json'),
                           source_json=data_json.get('source_json'),
                           error=error
                           )


@views.route('/index_static', methods=['GET', 'POST'])
def index_static_page():
    return render_template("index_static.html")


@views.route("/data", methods=["GET"])
def get_data():
    return {'id': 1, 'test': 'test'}
