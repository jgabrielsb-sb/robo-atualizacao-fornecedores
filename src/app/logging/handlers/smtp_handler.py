from logging.handlers import SMTPHandler
import logging

class DynamicSubjectSMTPHandler(SMTPHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord):
        self.subject = f'[Robô Atualização de Fornecedores] - Erro {record.name}'
        super().emit(record)