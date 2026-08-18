import logging
import app.logging.logger
import schedule
import time

from app.composition.container import Container
from config.settings import settings

container = Container()
use_case = container.get_get_and_update_fornecedores_workflow()

logger = logging.getLogger("main")

def run_workflow():
    logger.info("Running workflow")
    use_case.run()

schedule.every().day.at(settings.RUN_CRON_TIME).do(run_workflow)

if __name__ == "__main__":
    logger.info("Starting main")
    while True:
        time.sleep(30)
    # try:
    #     if settings.RUN_WITH_CRON:
    #         while True:
    #             schedule.run_pending()
    #             time.sleep(1)
    #     else:
    #         run_workflow()
    # except Exception as e:
    #     logger.critical("CRITICAL System Error", exc_info=True)
    #     raise e
    # finally:
    #     logger.info("System shutdown complete")


        
