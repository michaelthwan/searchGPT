from flask import Blueprint, render_template, request
from SearchGPTService import SearchGPTService

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@views.route('/index', methods=['GET'])
def index_page():
    search_text = request.values.get('q')
    data_json = {'response_json': [], 'source_json': []}
    if search_text is not None:
        search_gpt_service = SearchGPTService()
        response_text, response_text_with_footnote, source_text, data_json = search_gpt_service.query_and_get_answer(search_text)
    return render_template("index.html",
                           search_text=search_text or "Please search for something.",
                           response_json=data_json.get('response_json'),
                           source_json=data_json.get('source_json'),
                           )


@views.route('/index_static', methods=['GET', 'POST'])
def index_static_page():
    return render_template("index_static.html")


@views.route("/data", methods=["GET"])
def get_data():
    return {'id': 1, 'test': 'test'}
