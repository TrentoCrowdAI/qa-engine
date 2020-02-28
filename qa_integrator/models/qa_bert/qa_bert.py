import json
import os
import copy
import uuid

from . import qa_constants

OUT_PREDICTION_FILE = "model_out_prediction_formatted.json"
STATUS_COMPLETED_FILE = "completed.txt"
STATUS_FAILED_FILE = "failed.txt"


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
                  --init_checkpoint=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/model_latest.ckpt-0 \
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


def get_training_file_formatted(document_questions):

    qas = []
    for question_answer in document_questions['question_answers']:
        qas.append({
            'id': str(uuid.uuid4()),
            'question': question_answer['question'],
            'answers': question_answer['answers']
        })
    document = {
        'context': document_questions['document_text'],
        'qas': qas,
    }
    obj = {
        'title': document_questions['document_title'],
        'paragraphs': [document],
    }
    return obj


def do_training(documents_questions, training_dir):
    if not os.path.exists(training_dir):
        os.makedirs(training_dir)

    training_file = training_dir + "/my_file_qa.json"
    training_documents = []
    for document_questions in documents_questions:
        training_documents.append(get_training_file_formatted(document_questions))

    with open(training_file, "w") as f:
        json.dump({"data": training_documents}, f)

    return_value = os.system("python " + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-qa/run_squad.py \
                  --vocab_file=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/bert_base/vocab.txt \
                  --bert_config_file=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/bert_base/bert_config.json \
                  --init_checkpoint=" + qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/model_latest.ckpt-0 \
                  --do_train=True \
                  --train_file=" + training_file + "\
                  --do_predict=False \
                  --train_batch_size=32 \
                  --learning_rate=3e-5 \
                  --num_train_epochs=2.0 \
                  --max_seq_length=384 \
                  --doc_stride=128 \
                  --output_dir=" + training_dir)

    os.rename(training_dir + "/model.ckpt-0.meta", qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/model_latest.ckpt-0.meta")
    os.rename(training_dir + "/model.ckpt-0.index", qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/model_latest.ckpt-0.index")
    os.rename(training_dir + "/model.ckpt-0.data-00000-of-00001", qa_constants.QA_BERT_MODEL_BASE_DIR + "/bert-model/model_latest.ckpt-0.data-00000-of-00001")

    print('Training return value: ' + str(return_value))

    # Disabled because training returns "Killed" status...
    # if return_value != 0:
    #     with open(training_dir + "/" + STATUS_FAILED_FILE, "w") as f:
    #         json.dump({}, f)

    with open(training_dir + "/" + STATUS_COMPLETED_FILE, "w") as f:
        json.dump({}, f)

    return True


def is_training_completed(training_dir):
    training_file = os.path.join(training_dir, STATUS_COMPLETED_FILE)
    return os.path.exists(training_file)


def training_completed_at(training_dir):
    training_file = os.path.join(training_dir, STATUS_COMPLETED_FILE)
    return os.path.getmtime(training_file)
