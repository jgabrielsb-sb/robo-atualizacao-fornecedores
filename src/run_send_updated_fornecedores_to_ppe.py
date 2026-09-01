from app.composition.container import Container

container = Container()
workflow = container.get_send_updated_fornecedores_to_ppe_workflow()
result = workflow.run()
print(result)
