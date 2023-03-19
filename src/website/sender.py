from flask import render_template

MSG_TYPE_SEARCH_STEP = 'search-step'
MSG_TYPE_OPEN_AI_STREAM = 'openai-stream'

# global var to store progress. Native polling 'socket'
exporting_progress = {}


class Sender:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.received_step_events = []
        self.openai_stream = ''
        self.search_result_step_html = ''

    def send_message(self, msg_type, msg: str):
        if msg_type == MSG_TYPE_SEARCH_STEP:
            self.received_step_events.append(msg)
            self.search_result_step_html = render_template('search_result_step.html',
                                                           search_result_step_json=[{'msg': received_msg} for received_msg in self.received_step_events])
        elif msg_type == MSG_TYPE_OPEN_AI_STREAM:
            self.openai_stream += msg
        else:
            pass
        global exporting_progress
        exporting_progress[self.request_id] = {'html': self.search_result_step_html,
                                               'openai_stream': self.openai_stream}
