from crontab import CronTab
from config_util import config

try:
    cron = CronTab(user=True)
    cron.remove_all(comment=config.utils_auto_delete_cronjob.cronjob_name)
    cron.write()
except:
    print("An exception occurred setting the cronjob")
