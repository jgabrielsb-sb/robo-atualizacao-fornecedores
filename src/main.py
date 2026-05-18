from app.composition.container import Container
from app.infra.api_requester.protheus_api_requester.models import (
    ClassificacaoProtheus,
    FederacaoProtheus,
    FornecedorUpdateOnProtheus,
    SimplesNacionalProtheus,
    SimNaoProtheus,
    TipoFornecedorProtheus,
    VinculoSebraeProtheus,
    BancosProtheus,
)

container = Container()

result = container.adapter_provider.get_get_cnpjs_to_update_via_fornecedores_api_adapter().get()
print(result)



# protheus_requester = container.infra_provider.get_protheus_api_requester()

# fornecedor = FornecedorUpdateOnProtheus(
#     Nome_For="ZUCCA BUFFET LTDA.",
#     Nome_Red="ZUCCA",
#     CNPJ_For="26235452000146",
#     Ende_For="Rua Olavo Macedo Ribeiro",
#     Nume_End="37",
#     Cmpl_End="",
#     Bair_For="Jatiuca",
#     Esta_For="AL",
#     Codi_Mun="04302",
#     Muni_For="MACEIO",
#     CEP_Forn="57036830",
#     DDD_Forn="82",
#     Tel_Forn="999683300",
#     Ema_Forn="brenolopesdefarias@gmail.com",
#     Tipo_Forn=TipoFornecedorProtheus.PESSOA_JURIDICA,
#     Classifi=ClassificacaoProtheus.MEI,
#     Insc_Est="ISENTO",
#     For_Ativ=SimNaoProtheus.SIM,
#     Simples=SimplesNacionalProtheus.NAO,
#     Cod_Rete="1708",
#     Vinc_Seb=VinculoSebraeProtheus.SEM_VINCULO,
#     Federaca=FederacaoProtheus.NAO,
#     Cooperat=SimNaoProtheus.NAO,
    
# )

# result = protheus_requester.update_fornecedor(fornecedor)
# print(result)
