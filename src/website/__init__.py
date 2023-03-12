from flask import Flask
from flask_socketio import SocketIO

from app_context import AppContext


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_xyz'

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    socket_io = SocketIO(app)
    AppContext.set_socket_io(socket_io)

    return app
