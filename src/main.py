import logging
from datetime import datetime
import schedule
import time

from app.composition.container import Container
from config.settings import settings

import os,sys

## Supress all print statements and maintain just the logs
sys.stdout = open(os.devnull, 'w')

container = Container()
use_case = container.get_get_and_update_fornecedores_workflow()

logger = logging.getLogger("main")

def run_workflow():
    use_case.run()

def run_monthly_workflow():
    if datetime.now().day == 1:
        run_workflow()

def run_weekly_workflow():
    if datetime.now().weekday() == 0:  # Monday
        run_workflow()

RUN_EVERY_MONTH = False
RUN_EVERY_WEEK = True

if RUN_EVERY_MONTH:
    schedule.every().day.at(settings.RUN_CRON_TIME).do(run_monthly_workflow)
if RUN_EVERY_WEEK:
    schedule.every().day.at(settings.RUN_CRON_TIME).do(run_weekly_workflow)

if __name__ == "__main__":
    try:
        if settings.RUN_WITH_CRON:
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            run_workflow()
    except Exception as e:
        logger.critical("CRITICAL System Error", exc_info=True)
        raise e
    finally:
        logger.info("System shutdown complete")


        
