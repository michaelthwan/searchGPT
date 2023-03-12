from dataclasses import dataclass


@dataclass
class Message:
    msg_type: str
    msg: str
