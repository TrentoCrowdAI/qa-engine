from datetime import datetime
import os
import sys
import shutil
from config_util import config

predictions_root_dir = config.qa_engine.predictions_root_dir
PREDICTION_DELETE_AFTER_MINUTES = config.utils_auto_delete_cronjob.delete_older_than_minutes_predictions
PREDICTION_DELETE_LOG_FILE = os.path.join(predictions_root_dir, config.utils_auto_delete_cronjob.log_file_name)

trainings_root_dir = config.qa_engine.trainings_root_dir
TRAINING_DELETE_AFTER_MINUTES = config.utils_auto_delete_cronjob.delete_older_than_minutes_trainings
TRAINING_DELETE_LOG_FILE = os.path.join(trainings_root_dir, config.utils_auto_delete_cronjob.log_file_name)


def get_immediate_subdirectories(a_dir):
    return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def delete_in_folder(base_dir, log_file_name, delete_after_minutes):
    print("Now datetime:", datetime.now())
    log_file = open(log_file_name, "a")
    log_file.write("Executed script at: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "\n")

    for directory in get_immediate_subdirectories(base_dir):
        directory_last_edit_datetime = datetime.fromtimestamp(os.stat(directory).st_mtime)
        difference_from_now = (datetime.now() - directory_last_edit_datetime).total_seconds() / 60.0
        is_directory_to_delete = difference_from_now >= delete_after_minutes
        if is_directory_to_delete:
            shutil.rmtree(directory, ignore_errors=True)

        debug_string = directory + " last edit date:\t" + directory_last_edit_datetime.strftime(
            "%m/%d/%Y, %H:%M:%S") + "\tdifference in minutes:\t" + str(
            difference_from_now) + "\tdeleted:\t" + str(is_directory_to_delete)
        log_file.write(debug_string + "\n")
        print(debug_string)

    log_file.close()


delete_in_folder(predictions_root_dir, PREDICTION_DELETE_LOG_FILE, PREDICTION_DELETE_AFTER_MINUTES)
delete_in_folder(trainings_root_dir, TRAINING_DELETE_LOG_FILE, TRAINING_DELETE_AFTER_MINUTES)
