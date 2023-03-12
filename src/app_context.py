class AppContext:
    socket_io = None

    @classmethod
    def set_socket_io(cls, socket_io):
        cls.socket_io = socket_io
