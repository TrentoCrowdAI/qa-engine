import importlib
import os
from concurrent.futures.thread import ThreadPoolExecutor
from os import path
import shutil
import uuid
import threading
import json
from config_util import config

modules = []
PREDICTION_ROOT_DIR = config.qa_engine.predictions_root_dir
PREDICTION_TMP_DIR_PREFIX = PREDICTION_ROOT_DIR + "/prediction_"
PREDICTION_MODELS_REQUESTED_FILE = "models-requested.txt"


pool_executor = ThreadPoolExecutor(max_workers=config.qa_engine.predictions_thread_pool_executor_max_workers)

for model in config.qa_engine.models_available:
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
    if not os.path.exists(prediction_base_dir):
        os.makedirs(prediction_base_dir)

    prediction_request = {
        'id': prediction_request_id
    }

    prediction_models = []

    questions_formatted = [gen_question_entry(q) for q in questions]

    for module in modules:
        if ('all' in model_types) or (getattr(module, 'api_name') in model_types):
            prediction_models.append(getattr(module, 'api_name'))
            pool_executor.submit(module.do_prediction, texts, questions_formatted, prediction_base_dir + "/" + model['name'])

            # prediction_thread = threading.Thread(target=module.do_prediction,
            #                                      args=(texts, questions_formatted, prediction_base_dir + "/" + model['name']))
            # prediction_thread.start()

    with open(os.path.join(prediction_base_dir, PREDICTION_MODELS_REQUESTED_FILE), "w") as f:
        json.dump({"models": [",".join(prediction_models)]}, f)

    return prediction_request


def get_prediction(prediction_request_id, delete_prediction=False):
    prediction_base_dir = PREDICTION_TMP_DIR_PREFIX + prediction_request_id

    prediction_request = {
        'id': prediction_request_id
    }

    prediction_models = {}
    requested_models = []
    completed_models = []

    prediction_models_file = os.path.join(prediction_base_dir, PREDICTION_MODELS_REQUESTED_FILE)
    if not (path.exists(prediction_base_dir) and path.exists(prediction_models_file)):
        return None
    with open(prediction_models_file) as f:
        requested_models = json.load(f)["models"]

    for module in modules:
        if getattr(module, 'api_name') in requested_models:
            prediction, prediction_completed = module.get_prediction(os.path.join(prediction_base_dir, model['name']))
            prediction_models[getattr(module, 'api_name')] = prediction
            if prediction_completed:
                completed_models.append(getattr(module, 'api_name'))

    prediction_request['models_requested'] = requested_models
    prediction_request['models_completed'] = completed_models
    prediction_request['models'] = prediction_models

    if delete_prediction:
        shutil.rmtree(prediction_base_dir, ignore_errors=True)

    return prediction_request


def delete_prediction(prediction_id):
    prediction_base_dir = PREDICTION_TMP_DIR_PREFIX + prediction_id
    if not path.exists(prediction_base_dir):
        return None
    shutil.rmtree(prediction_base_dir, ignore_errors=True)
    return not path.exists(prediction_base_dir)


def gen_question_entry(q):
    return {
        "id": str(uuid.uuid4()),
        "question": q
    }
