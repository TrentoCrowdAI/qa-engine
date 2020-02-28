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

TRAINING_ROOT_DIR = config.qa_engine.trainings_root_dir
TRAINING_REQUEST_PREFIX = "training_"
TRAINING_TMP_DIR_PREFIX = TRAINING_ROOT_DIR + "/" + TRAINING_REQUEST_PREFIX

PREDICTION_MODELS_REQUESTED_FILE = "models-requested.txt"

pool_executor = ThreadPoolExecutor(max_workers=config.qa_engine.predictions_thread_pool_executor_max_workers)

for model in config.qa_engine.models_available:
    _temp = importlib.import_module("." + model['name'], model['from'])
    setattr(_temp, 'api_name', model['api_name'])
    print(_temp.test_function())
    modules.append(_temp)

if not os.path.exists(PREDICTION_ROOT_DIR):
    os.makedirs(PREDICTION_ROOT_DIR)
if not os.path.exists(TRAINING_ROOT_DIR):
    os.makedirs(TRAINING_ROOT_DIR)


def prepare_environment_thread_function():
    print("running prepare_environment.sh")
    os.system('/bin/bash prepare_environment.sh')


def prepare_environment():
    prepare_environment_thread = threading.Thread(target=prepare_environment_thread_function, args="")
    prepare_environment_thread.start()


def is_environment_ready():
    return path.exists("actual_models/ready_models_file.txt")


def do_prediction(documents, questions, model_types):
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
            pool_executor.submit(module.do_prediction, documents, questions_formatted,
                                 prediction_base_dir + "/" + model['name'])

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


def do_training(documents_questions, model_types):
    training_request_id = "request_" + str(uuid.uuid4())
    training_base_dir = TRAINING_TMP_DIR_PREFIX + training_request_id
    if not os.path.exists(training_base_dir):
        os.makedirs(training_base_dir)

    training_request = {
        'training_id': training_request_id
    }

    training_models = []

    for module in modules:
        if ('all' in model_types) or (getattr(module, 'api_name') in model_types):
            training_models.append(getattr(module, 'api_name'))
            pool_executor.submit(module.do_training, documents_questions, training_base_dir + "/" + model['name'])

    with open(os.path.join(training_base_dir, PREDICTION_MODELS_REQUESTED_FILE), "w") as f:
        json.dump({"models": [",".join(training_models)]}, f)

    return training_request


def get_training(training_request_id, delete_training=False):
    training_base_dir = TRAINING_TMP_DIR_PREFIX + training_request_id

    training_request = {
        'training_id': training_request_id
    }

    prediction_models_file = os.path.join(training_base_dir, PREDICTION_MODELS_REQUESTED_FILE)
    if not (path.exists(training_base_dir) and path.exists(prediction_models_file)):
        return None

    is_request_completed, finished_at, requested_models, completed_models = is_training_request_completed(
        training_request_id)

    queue_position = -1
    if not is_request_completed:
        queue_position = get_training_requests()['queue'].index(TRAINING_REQUEST_PREFIX + training_request_id)

    training_request['models_requested'] = requested_models
    training_request['models_completed'] = completed_models
    training_request['requested_at'] = int(
        os.stat(os.path.join(training_base_dir, PREDICTION_MODELS_REQUESTED_FILE)).st_mtime)
    training_request['finished_at'] = finished_at
    training_request['queue_position'] = queue_position

    if delete_training:
        shutil.rmtree(training_base_dir, ignore_errors=True)

    return training_request


def is_training_request_completed(training_request_id):
    training_base_dir = TRAINING_TMP_DIR_PREFIX + training_request_id

    requested_models = []
    completed_models = []

    prediction_models_file = os.path.join(training_base_dir, PREDICTION_MODELS_REQUESTED_FILE)
    with open(prediction_models_file) as f:
        requested_models = json.load(f)["models"]

    finished_at = 0

    for module in modules:
        if getattr(module, 'api_name') in requested_models:
            training_completed = module.is_training_completed(os.path.join(training_base_dir, model['name']))
            if training_completed:
                completed_models.append(getattr(module, 'api_name'))
                finished_at = max(finished_at,
                                  int(module.training_completed_at(os.path.join(training_base_dir, model['name']))))

    is_completed = len(requested_models) == len(completed_models)
    if not is_completed:
        finished_at = None

    return is_completed, finished_at, requested_models, completed_models


def get_training_requests(formatted=False):
    dirs = [s for s in os.listdir(TRAINING_ROOT_DIR) if os.path.isdir(os.path.join(TRAINING_ROOT_DIR, s))]
    dirs.sort(key=lambda s: os.path.getmtime(os.path.join(TRAINING_ROOT_DIR, s)))

    queue = []
    completed = []
    for dir in dirs:
        if not is_training_request_completed(dir[len(TRAINING_REQUEST_PREFIX):])[0]:
            queue.append(dir)
        else:
            completed.append(dir)

    def format_requests(dirs, formatted, show_position=False):
        if not formatted:
            return dirs
        else:
            formatted_dirs = []
            position_in_queue = 0
            for dir in dirs:
                formatted_dir = {
                    'training_id': dir,
                    'requested_at': int(
                        os.stat(os.path.join(TRAINING_ROOT_DIR, dir, PREDICTION_MODELS_REQUESTED_FILE)).st_mtime)
                }
                if show_position:
                    formatted_dir['queue_position'] = position_in_queue

                formatted_dirs.append(formatted_dir)
                position_in_queue = position_in_queue + 1
            return formatted_dirs

    return {
        'queue': format_requests(queue, formatted, show_position=True),
        'completed': format_requests(completed, formatted)
    }


def delete_training(training_id):
    training_base_dir = TRAINING_TMP_DIR_PREFIX + training_id
    if not path.exists(training_base_dir):
        return None
    shutil.rmtree(training_base_dir, ignore_errors=True)
    return not path.exists(training_base_dir)


def gen_question_entry(q):
    return {
        "id": str(uuid.uuid4()),
        "question": q
    }
