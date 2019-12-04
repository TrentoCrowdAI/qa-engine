import importlib
import os
from os import path
import shutil
import uuid
from . import qa_models_available
import threading

modules = []
PREDICTION_TMP_DIR_PREFIX = "tmpPrediction_"

for model in qa_models_available.models_available:
    _temp = importlib.import_module("." + model['name'], model['from'])
    setattr(_temp, 'api_name', model['api_name'])
    print(_temp.test_function())
    modules.append(_temp)


def prepare_environment_thread_function():
    print("running prepare_environment.sh")
    os.system('/bin/bash prepare_environment.sh')


def prepare_environment():
    prepare_environment_thread = threading.Thread(target=prepare_environment_thread_function, args="")
    prepare_environment_thread.start()


def is_environment_ready():
    return path.exists("actual_models/ready_models_file.txt")


def do_prediction(texts, questions, model_types):
    prediction_request_id = "request_" + str(uuid.uuid4())
    prediction_base_dir = PREDICTION_TMP_DIR_PREFIX + prediction_request_id

    prediction_request = {
        'id': prediction_request_id
    }

    prediction_models = {}

    questions_formatted = [gen_question_entry(q) for q in questions]

    for module in modules:
        if ('all' in model_types) or (getattr(module, 'api_name') in model_types):
            prediction_thread = threading.Thread(target=module.do_prediction,
                                                 args=(texts, questions_formatted, prediction_base_dir + "/" + model['name']))
            prediction_thread.start()
            #prediction_models[getattr(module, 'api_name')] = module.do_prediction(texts, questions_formatted, prediction_base_dir + "/" + model['name'])

    #prediction_request['models'] = prediction_models

    return prediction_request


def get_prediction(prediction_request_id, delete_prediction=False):
    prediction_base_dir = PREDICTION_TMP_DIR_PREFIX + prediction_request_id

    prediction_request = {
        'id': prediction_request_id
    }

    prediction_models = {}

    for module in modules:
        prediction_models[getattr(module, 'api_name')] = module.get_prediction(prediction_base_dir + "/" + model['name'])

    prediction_request['models'] = prediction_models

    if delete_prediction:
        shutil.rmtree(prediction_base_dir, ignore_errors=True)

    return prediction_request


def gen_question_entry(q):
    return {
        "id": str(uuid.uuid4()),
        "question": q
    }
