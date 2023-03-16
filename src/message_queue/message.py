from dataclasses import dataclass


@dataclass
class Message:
    sender_id: str
    msg_type: str
    msg: str
