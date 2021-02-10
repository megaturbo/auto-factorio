import os

from flask import Flask, render_template, request, jsonify

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
    return jsonify(exoscale.start_machine())


# stops server. returns a job_id, use /job_status to check job status
@app.route('/stop', methods=['POST'])
def stop():
    return jsonify(exoscale.stop_machine())


@app.route('/job_status', methods=['GET'])
def job_status():
    job_id = request.args.get('job_id')
    return jsonify(exoscale.job_result(job_id))


if __name__ == '__main__':
    app.run(debug=True)
