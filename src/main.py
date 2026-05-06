import logging

from app.composition.container import Container

logger = logging.getLogger(__name__)


def main() -> None:
    container = Container()
    logger.info("Iniciando robo-atualizacao-fornecedores...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
