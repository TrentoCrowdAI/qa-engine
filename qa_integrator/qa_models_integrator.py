import shutil
import uuid
import qa_models_available
import threading

modules = []
PREDICTION_TMP_DIR_PREFIX = "tmpPrediction_"

for model in qa_models_available.models_available:
    print("Importing model: " + model['from'])
    _temp = __import__(model['from'], {"__name__": __name__}, locals(), [model['name']], -1)
    _module = getattr(_temp, model['name'])
    setattr(_module, 'api_name', model['api_name'])
    modules.append(_module)


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
