from flask import Blueprint, render_template

MSG_TYPE_SEARCH_STEP = 'search-step'
MSG_TYPE_OPEN_AI_STREAM = 'openai-stream'

# global var to store progress. Native polling 'socket'
exporting_progress = {}

class Sender:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.received_step_events = []

    def send_message(self, msg_type, msg: str):
        if msg_type == MSG_TYPE_SEARCH_STEP:
            self.received_step_events.append(msg)
            search_result_step_html = render_template('search_result_step.html',
                                                      search_result_step_json=[{'msg': received_msg} for received_msg in self.received_step_events])
        else:
            search_result_step_html = []
        global exporting_progress
        exporting_progress[self.request_id] = search_result_step_html

        print("exporting_progress in sender.py")
        print(exporting_progress)

        # TODO: when to delete msg
        # TODO: MSG_TYPE_OPEN_AI_STREAM
