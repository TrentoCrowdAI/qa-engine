import os
from flask import Flask, request
from qa_integrator import qa_models_integrator
from flask_swagger import swagger

qa_models_integrator.prepare_environment()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/documentation")
def spec():
    swag = swagger(app, from_file_keyword='swagger_from_file')
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "QA-Engine"
    return swag


@app.route('/api/test_resources_status')
def test_model_dir():
    """
        swagger_from_file: yaml/test_resources_status.yml
    """
    actual_models_dir_present = os.path.isdir('actual_models')
    bert_model_dir_present = os.path.isdir('actual_models/bert-model')
    to_rtn = {
        "environment_ready": qa_models_integrator.is_environment_ready(),
        "actual_models_dir": actual_models_dir_present,
        "bert-model": bert_model_dir_present,
        "root_files": os.listdir(),
        "actual_models_files": os.listdir('actual_models') if actual_models_dir_present else []
    }
    return to_rtn


@app.route('/api/prepare_environment')
def prepare_environment():
    qa_models_integrator.prepare_environment()
    to_rtn = {
        "msg": "Environment is preparing... Call /api/test_resources_status to check the status"
    }
    return to_rtn


@app.route('/api/prediction', methods=['POST'])
def do_prediction():
    """
        swagger_from_file: yaml/prediction_request.yml
    """
    if not qa_models_integrator.is_environment_ready():
        return {
            "msg": "Environment resources not ready, please try again later."
        }, 503

    texts_param = get_param(request.json, 'source_texts', required=True)
    questions_param = get_param(request.json, 'questions', required=True)
    model_types_param = get_param(request.json, 'models', required=True)

    missing_params = check_params([texts_param, questions_param, model_types_param])
    if missing_params:
        return {"missing_required_params": missing_params}, 400

    prediction_request = qa_models_integrator.do_prediction(texts_param['value'], questions_param['value'], model_types_param['value'].split(','))
    return prediction_request


@app.route('/api/prediction', methods=['GET'])
def get_prediction():
    """
        swagger_from_file: yaml/prediction_completed.yml
    """
    if not qa_models_integrator.is_environment_ready():
        return {
            "msg": "Environment resources not ready, please try again later."
        }, 503

    prediction_request_id_param = get_param(request.args, 'prediction_request_id', required=True)
    delete_prediction_param = get_param(request.args, 'delete_prediction', required=False, function_for_value=str2bool)

    missing_params = check_params([prediction_request_id_param, delete_prediction_param])
    if missing_params:
        return {"missing_required_params": missing_params}, 400

    prediction = qa_models_integrator.get_prediction(prediction_request_id_param['value'], delete_prediction_param['value'])

    return prediction


@app.route('/api/models', methods=['GET'])
def get_models():
    """
        swagger_from_file: yaml/models_get.yml
    """
    models = []
    for model in qa_models_integrator.qa_models_available.models_available:
        models.append({
            "api_name": model['api_name']
        })

    return {"available_models": models}


def get_param(from_source, param_name, required=False, function_for_value=None):
    obj = {
        "name": param_name,
        "required": required,
        "value": from_source.get(param_name)
    }
    if function_for_value:
        obj["value"] = function_for_value(obj["value"])
    return obj


def check_params(params):
    missing_params = []
    for required_param in params:
        if not check_required_param(required_param["value"]):
            missing_params.append(required_param)
    return missing_params


def str2bool(v):
    if v is None:
        return False
    return v.lower() in ("yes", "true", "t", "1")


def check_required_param(param):
    return param is not None


if __name__ == '__main__':
    app.run()

#TODO: API documentation (Swagger)
#TODO: model integration documentation
#TODO: train model API

#TODO: cron job to delete tmp dir
#TODO: threadpool executor?