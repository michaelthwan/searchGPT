from flask import Blueprint, render_template

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@views.route('/index', methods=['GET', 'POST'])
def index_page():
    return render_template("index.html")


@views.route('/index_static', methods=['GET', 'POST'])
def index_static_page():
    return render_template("index_static.html")


@views.route("/data", methods=["GET"])
def get_data():
    return {'id': 1, 'test': 'test'}
