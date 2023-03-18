from flask import Flask
from flask_socketio import SocketIO


class SearchGPTContext:
    app: Flask = None
    socket_io: SocketIO = None

    @classmethod
    def set_app(cls, app: Flask):
        cls.app = app

    @classmethod
    def set_socket_io(cls, socket_io: SocketIO):
        cls.socket_io = socket_io
