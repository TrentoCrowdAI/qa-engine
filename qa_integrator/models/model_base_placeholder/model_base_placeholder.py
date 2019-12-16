import os
import json

OUT_PREDICTION_FILE = "model_out_prediction_formatted.json"

# This python package must expose 3 functions that are used by the integrator:
# - test_function()
# - do_prediction(texts, questions_formatted, prediction_dir)
# - get_prediction(prediction_dir)
#
# || STEPS TO CREATE A COMPATIBLE MODEL ||
#
# 1. Search for ----> letter. <---- comments in this file
# 2. Compile A.
# 3. Write the specific code for B, C, D, E points
# 4. Check correctness of point F
# 5. Edit import statement inside __init__.py with this file name
# 6. To make the model available to the integrator, edit the file config.json adding an object of this type in the qa_engine.models_available array:
#      {
#         "from": "qa_integrator.models", # Position of the model used by the integrator
#         "name": "qa_bert", # Name of the model to import
#         "api_name": "qa_bert" # Name of the model to be exposed/accessed by the service APIs
#     }


def test_function():
    # ----> A. SET THE MODEL NAME, THIS FUNCTION IS USED TO DEBUG THE CORRECTNESS OF THE IMPORT FROM THE INTEGRATOR <----
    return "Model BASE PLACEHOLDER imported correctly"


def do_prediction(texts, questions_formatted, prediction_dir):
    """
       Start a prediction

       :param list str texts: An array of strings with the source text from where the predictor must search answers
       :param list str questions_formatted: An array of strings with the questions to be asked to the engine
       :param str prediction_dir: The base prediction dir to use for this prediction
    """

    if not os.path.exists(prediction_dir):
        os.makedirs(prediction_dir)

    prediction_file = os.path.join(prediction_dir, "my_file_qa.json")

    # ----> B. WRITE THE CODE TO PREPARE THE PREDICTION REQUEST <----
    # EXAMPLE:
    # prediction_file_content = get_prediction_file_formatted(texts, questions_formatted)
    # with open(prediction_file, "w") as f:
    #     json.dump({"data": [prediction_file_content]}, f)

    # ----> C. WRITE THE CODE TO START THE PREDICTION <----
    # EXAMPLE:
    # os.system("path_to_predictor/predictor_model/run_prediction.sh --output_dir=" + prediction_dir)

    # ----> D. WRITE THE CODE TO READ THE ANSWERS PRODUCED <----
    # EXAMPLE:
    # with open(prediction_dir + "/predictions.json") as json_file:
    #     answers = json.load(json_file)

    complete_predictions = []
    # ----> E. WRITE THE CODE TO WRITE A FILE WITH ANSWERS FORMATTED FOR THE QA_INTEGRATOR ENGINE <----
    # EXAMPLE:
    # for answer in answers:
    #     complete_answer = {
    #         "id": answer["question_id"],
    #         "question": answer["question_text"],
    #         "answer": answer["answer"]
    #     }
    #     complete_predictions.append(complete_answer)

    # with open(prediction_dir + "/" + OUT_PREDICTION_FILE, "w") as f:
    #     json.dump(complete_predictions, f)

    return complete_predictions


def get_prediction(prediction_dir):
    """
           Get the prediction result

           :param str prediction_dir: The base prediction dir used for this prediction
    """
    out_prediction = {}
    prediction_completed = False

    # ----> F. WRITE THE CODE TO READ THE FILE WITH ANSWERS FORMATTED FOR THE QA_INTEGRATOR ENGINE
    # AND RETURN AN ARRAY WITH ANSWERS, AND A BOOLEAN THAT INDICATE IF THE PREDICTION IS FINISHED <----
    # EXAMPLE, CHECK CORRECTNESS:

    pred_file = os.path.join(prediction_dir, OUT_PREDICTION_FILE)

    if os.path.exists(pred_file):
        prediction_completed = True
        with open(pred_file) as json_file:
            out_prediction = json.load(json_file)

    return out_prediction, prediction_completed
