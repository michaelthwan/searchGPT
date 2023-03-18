from flask import Flask
from flask_socketio import SocketIO

from app_context import SearchGPTContext


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_xyz'

    SearchGPTContext.set_app(app)

    socket_io: SocketIO = SocketIO(app)
    SearchGPTContext.set_socket_io(socket_io)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    return app
