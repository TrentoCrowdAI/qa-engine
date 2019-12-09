from crontab import CronTab

try:
    cron = CronTab(user=True)
    cron.remove_all(comment='qa_engine_delete_unused_predictions_cron')
    cron.write()
except:
    print("An exception occurred setting the cronjob")
