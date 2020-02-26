import json
import os
import copy
from . import qa_constants

OUT_PREDICTION_FILE = "model_out_prediction_formatted.json"


def test_function():
    return "Model BERT imported correctly"


def do_prediction(documents, questions_formatted, prediction_dir):
    if not os.path.exists(prediction_dir):
        os.makedirs(prediction_dir)

    prediction_file = prediction_dir + "/my_file_qa.json"
    prediction_documents = []
    documents_ids = []
    for document in documents:
        documents_ids.append(document['id'])
        prediction_documents.append(get_prediction_file_formatted(document['text'], document['id'], questions_formatted))

    with open(prediction_file, "w") as f:
        json.dump({"data": prediction_documents}, f)

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
    for document_id in documents_ids:
        for question in questions_formatted:
            complete_answer = {
                "document_id": document_id,
                "question_id": question["id"],
                "question": question["question"],
                "answer": answers[document_id + "_" + question["id"]]
            }
            complete_predictions.append(complete_answer)

    with open(prediction_dir + "/" + OUT_PREDICTION_FILE, "w") as f:
        json.dump(complete_predictions, f)

    return complete_predictions


def get_prediction_file_formatted(text, document_id, questions_formatted):
    qas = copy.deepcopy(questions_formatted)
    for question in qas:
        question['id'] = document_id + "_" + question['id']
    paragraphs = [{
        "context": text,
        "qas": qas
    }]

    output = {
        "title": "Test Title",
        "paragraphs": paragraphs
    }
    return output


def get_prediction(prediction_dir):
    out_prediction = {}
    prediction_completed = False

    pred_file = os.path.join(prediction_dir, OUT_PREDICTION_FILE)

    if os.path.exists(pred_file):
        prediction_completed = True
        with open(pred_file) as json_file:
            out_prediction = json.load(json_file)

    return out_prediction, prediction_completed
