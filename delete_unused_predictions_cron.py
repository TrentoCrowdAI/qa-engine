from datetime import datetime
import os
import sys
import shutil
from config_util import config

prediction_root_dir = sys.argv[1]
PREDICTION_DELETE_AFTER_MINUTES = config.utils_auto_delete_cronjob.delete_older_than_minutes
PREDICTION_DELETE_LOG_FILE = os.path.join(prediction_root_dir, config.utils_auto_delete_cronjob.log_file_name)


def get_immediate_subdirectories(a_dir):
    return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


print("Now datetime:", datetime.now())
log_file = open(PREDICTION_DELETE_LOG_FILE, "a")
log_file.write("Executed script at: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "\n")

for directory in get_immediate_subdirectories(prediction_root_dir):
    directory_last_edit_datetime = datetime.fromtimestamp(os.stat(directory).st_mtime)
    difference_from_now = (datetime.now() - directory_last_edit_datetime).total_seconds() / 60.0
    is_directory_to_delete = difference_from_now >= PREDICTION_DELETE_AFTER_MINUTES
    if is_directory_to_delete:
        shutil.rmtree(directory, ignore_errors=True)

    debug_string = directory + " last edit date:\t" + directory_last_edit_datetime.strftime(
        "%m/%d/%Y, %H:%M:%S") + "\tdifference in minutes:\t" + str(
        difference_from_now) + "\tdeleted:\t" + str(is_directory_to_delete)
    log_file.write(debug_string + "\n")
    print(debug_string)

log_file.close()
