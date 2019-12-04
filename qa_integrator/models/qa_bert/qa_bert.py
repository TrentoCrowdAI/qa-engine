import json
import os
from . import qa_constants

OUT_PREDICTION_FILE = "model_out_prediction_formatted.json"


def test_function():
    return "Model BERT imported correctly"


def do_prediction(texts, questions_formatted, prediction_dir):
    if not os.path.exists(prediction_dir):
        os.makedirs(prediction_dir)

    prediction_file = prediction_dir + "/my_file_qa.json"
    prediction_file_content = get_prediction_file_formatted(texts, questions_formatted)

    with open(prediction_file, "w") as f:
        json.dump({"data": [prediction_file_content]}, f)

    os.system("python " + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-qa/run_squad.py \
                  --vocab_file=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/bert_base/vocab.txt \
                  --bert_config_file=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/bert_base/bert_config.json \
                  --init_checkpoint=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/model.ckpt-5474 \
                  --do_train=False \
                  --train_file=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/squad_dir/train-v1.1.json \
                  --do_predict=True \
                  --predict_file=" + prediction_file + "\
                  --train_batch_size=32 \
                  --learning_rate=3e-5 \
                  --num_train_epochs=2.0 \
                  --max_seq_length=384 \
                  --doc_stride=128 \
                  --output_dir=" + prediction_dir)
    with open(prediction_dir + "/predictions.json") as json_file:
        answers = json.load(json_file)

    complete_predictions = []
    for paragraph in prediction_file_content["paragraphs"]:
        for question in paragraph["qas"]:
            complete_answer = {
                "id": question["id"],
                "question": question["question"],
                "answer": answers[question["id"]]
            }
            complete_predictions.append(complete_answer)

    with open(prediction_dir + "/" + OUT_PREDICTION_FILE, "w") as f:
        json.dump(complete_predictions, f)

    return complete_predictions


def get_prediction_file_formatted(texts, questions_formatted):
    paragraphs = []
    for text in texts:
        paragraphs.append(
            {
                "context": text,
                "qas": questions_formatted
            }
        )

    output = {
        "title": "Test Title",
        "paragraphs": paragraphs
    }
    return output


def get_prediction(prediction_dir):
    obj_to_return = {
        'prediction_completed': False,
        'prediction': {}
    }

    pred_file = prediction_dir + "/" + OUT_PREDICTION_FILE

    if os.path.exists(pred_file):
        obj_to_return['prediction_completed'] = True
        with open(pred_file) as json_file:
            out_prediction = json.load(json_file)
        obj_to_return['prediction'] = out_prediction

    return obj_to_return
