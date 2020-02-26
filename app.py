import os
from flask import Flask, request
from qa_integrator import qa_models_integrator
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from crontab import CronTab

from config_util import config

qa_models_integrator.prepare_environment()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


# Swagger specific
@app.route("/api/swagger-descriptor")
def spec():
    swag = swagger(app, from_file_keyword='swagger_from_file')
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "QA-Engine"
    return swag


SWAGGER_URL = '/swagger-ui'
API_URL = '/api/swagger-descriptor'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "QA-engine Swagger-UI"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
# end Swagger specific


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


@app.route('/api/predictions', methods=['POST'])
def do_prediction():
    """
        swagger_from_file: yaml/prediction_request.yml
    """
    if not qa_models_integrator.is_environment_ready():
        return {
            "msg": "Environment resources not ready, please try again later."
        }, 503

    documents_param = get_param(request.json, 'documents', required=True)
    questions_param = get_param(request.json, 'questions', required=True)
    model_types_param = get_param(request.json, 'models', required=True)

    missing_params = check_params([documents_param, questions_param, model_types_param])
    if missing_params:
        return {"missing_required_params": missing_params}, 400

    prediction_request = qa_models_integrator.do_prediction(documents_param['value'], questions_param['value'], model_types_param['value'])
    return prediction_request


@app.route('/api/predictions/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """
        swagger_from_file: yaml/prediction_completed.yml
    """
    if not qa_models_integrator.is_environment_ready():
        return {
            "msg": "Environment resources not ready, please try again later."
        }, 503

    prediction = qa_models_integrator.get_prediction(prediction_id)
    if not prediction:
        return {"msg": "prediction request id not found"}, 404

    return prediction


@app.route('/api/predictions/<prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    """
        swagger_from_file: yaml/prediction_delete.yml
    """
    if not qa_models_integrator.is_environment_ready():
        return {
            "msg": "Environment resources not ready, please try again later."
        }, 503

    result_successful = qa_models_integrator.delete_prediction(prediction_id)
    if result_successful is None:
        return {"msg": "prediction request id not found"}, 404
    if not result_successful:
        return {"msg": "something went wrong deleting, try again later"}, 503

    return "deleted successfully"


@app.route('/api/models', methods=['GET'])
def get_models():
    """
        swagger_from_file: yaml/models_get.yml
    """
    models = []
    for model in config.qa_engine.models_available:
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


# Start Cron job to delete predictions directory
try:
    cron = CronTab(user=True)
    cron.remove_all(comment='qa_engine_delete_unused_predictions_cron')
    job = cron.new(
        command='python ' + os.getcwd() + '/delete_unused_predictions_cron.py ' + os.getcwd() + '/' + qa_models_integrator.PREDICTION_ROOT_DIR,
        comment=config.utils_auto_delete_cronjob.cronjob_name)
    job.minute.every(config.utils_auto_delete_cronjob.job_every_n_minutes)

    cron.write()
except:
    print("An exception occurred setting the cronjob")

if __name__ == '__main__':
    app.run()
