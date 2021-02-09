import os
from urllib.parse import urlencode

from flask import Flask, render_template, request

from exoscale import Exoscale

app = Flask(__name__)

SERVER_ID = os.environ.get('FACTORIO_SERVER_ID')
API_KEY = os.environ.get('EXOSCALE_API_KEY')
API_SECRET = os.environ.get('EXOSCALE_API_SECRET')

exoscale = Exoscale(SERVER_ID, API_KEY, API_SECRET)


@app.route('/')
def index():
    is_running = exoscale.is_machine_running()
    button_text = "stop" if is_running else "start"
    form_action = "/" + button_text

    return render_template(
        'index.html',
        button_text=button_text,
        form_action=form_action,
        server_id=SERVER_ID,
        is_running=is_running
    )


# starts server. returns a job_id, use /job_status to check job status
@app.route('/start', methods=['POST'])
def start():
    return exoscale.start_machine()


# stops server. returns a job_id, use /job_status to check job status
@app.route('/stop', methods=['POST'])
def stop():
    return exoscale.stop_machine()


@app.route('/job_status', methods=['GET'])
def job_status():
    job_id = request.args.get('job_id')
    return exoscale.job_result(job_id)


if __name__ == '__main__':
    app.run(debug=True)
