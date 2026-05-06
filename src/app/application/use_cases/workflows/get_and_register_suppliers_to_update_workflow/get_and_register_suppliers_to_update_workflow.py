class GetAndRegisterFornecedoresToUpdateWorkflow:
    def __init__(
        self,
        get_fornecedores_to_update: "GetFornecedoresToUpdatePort",
        fornecedores_to_update_repository: "FornecedoresToUpdateRepositoryPort",
        event_publisher: "EventPublisherPort"
    ):
        self._get_fornecedores_to_update = get_fornecedores_to_update
        self._fornecedores_to_update_repository = fornecedores_to_update_repository
        self._event_publisher = event_publisher

    def get_fornecedores_to_update(self) -> FornecedoresToUpdate:
        try:
            self._get_fornecedores_to_update().get()
            self._event_publisher.publish(
                Event()
            )
        except Exception as e:
            self._event_publisher.publish(
                Event()
            )
            return StepResult()

    def save_fornecedores_to_update(self) -> StepResult:
        try:
            self._fornecedores_to_update_repository().save()
            self._event_publisher.publish(
                Event()
            )
        except Exception as e:
            self._event_publisher.publish(
                Event()
            )
            return StepResult()

    def run(self):


        

