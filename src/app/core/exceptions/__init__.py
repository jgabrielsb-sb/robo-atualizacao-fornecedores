class RoboBaseException(Exception):
    pass


class FornecedorNaoEncontradoException(RoboBaseException):
    pass


class ConsultaCNPJException(RoboBaseException):
    pass


class AtualizacaoFornecedorException(RoboBaseException):
    pass


class APIException(RoboBaseException):
    pass


class ConfiguracaoInvalidaException(RoboBaseException):
    pass
