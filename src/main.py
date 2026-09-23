import logging
import app.logging.logger
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

schedule.every().day.at(settings.RUN_CRON_TIME).do(run_workflow)

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


        
