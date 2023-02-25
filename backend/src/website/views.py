from flask import Blueprint, render_template, request
from SearchGPTService import SearchGPTService

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@views.route('/index', methods=['GET'])
def index_page():
    query = request.values.get('q')
    response_json = []
    if query is not None:
        search_gpt_service = SearchGPTService()
        response_text, response_text_with_footnote, source_text, response_json = search_gpt_service.query_and_get_answer(query)
    return render_template("index.html",
                           response_json=response_json,
                           )


@views.route('/index_static', methods=['GET', 'POST'])
def index_static_page():
    return render_template("index_static.html")


@views.route("/data", methods=["GET"])
def get_data():
    return {'id': 1, 'test': 'test'}
