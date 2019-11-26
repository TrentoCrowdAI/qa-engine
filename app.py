import os
import uuid

from flask import Flask, request
from qa_integrator import qa_models_integrator

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/text_model_dir')
def hello_world():
    return os.path.isdir('actual_models')


@app.route('/api/prediction', methods=['POST'])
def do_prediction():
    texts = request.json.get('source_texts')
    questions = request.json.get('questions')
    model_types = request.json.get('models')

    prediction_request = qa_models_integrator.do_prediction(texts, questions, model_types.split(','))

    return prediction_request


@app.route('/api/prediction', methods=['GET'])
def get_prediction():
    prediction_request_id = request.args.get('prediction_request_id')
    delete_prediction = str2bool(request.args.get('delete_prediction'))
    prediction = qa_models_integrator.get_prediction(prediction_request_id, delete_prediction)

    return prediction


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == '__main__':
    app.run()


#TODO: API documentation (Swagger)
#TODO: model integration documentation
#TODO: train model API
#TODO: API data validation

#TODO: cron job to delete tmp dir
#TODO: api to expose models name, and add "models_completed": true in the response json
#TODO: threadpool executor?
