from flask_socketio import SocketIO


class AppContext:
    socket_io: SocketIO = None

    @classmethod
    def set_socket_io(cls, socket_io: SocketIO):
        cls.socket_io = socket_io
