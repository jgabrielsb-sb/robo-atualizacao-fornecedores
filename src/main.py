import logging
import app.logging.logger
import schedule
import time

from app.composition.container import Container

container = Container()
use_case = container.get_get_and_update_fornecedores_workflow()

logger = logging.getLogger("main")

def run_workflow():
    logger.info("Running workflow")
    use_case.run()

schedule.every().second.do(run_workflow)

if __name__ == "__main__":
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logger.critical("CRITICAL System Error", exc_info=True)
        raise e
    finally:
        logger.info("System shutdown complete")

