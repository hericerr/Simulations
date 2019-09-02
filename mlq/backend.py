"""
Minimalistic app analyzing the sentiment using VADER (pre-trained from NLTK)
"""
from flask import Flask, request, jsonify
from mlq.queue import MLQ


app = Flask(__name__)

# redis queue - assumes redis already running on port 6379
mlq = MLQ('anakin', 'localhost', 6379, 0)


@app.route('/api/check_progress/<job_id>', methods=['GET'])
def check_progress(job_id):
    progress = mlq.get_progress(job_id)
    return progress


@app.route('/api/result/<job_id>', methods=['GET'])
def get_result(job_id):
    job = mlq.get_job(job_id)
    return jsonify(job['result']) or '[not available yet]'


@app.route('/api/submit', methods=['POST'])
def submit_job():
    job_id = mlq.post(request.get_json())
    return job_id
