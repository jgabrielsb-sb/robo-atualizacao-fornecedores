# Why Test the Adapters — The QA Engineer's Perspective

## 1. Where You Stand Now

You have built two layers of tests:

**Unit tests** verify logic in isolation. Every dependency is replaced with a fake. No HTTP call happens. The tests are fast, deterministic, and precise. They tell you that the filtering logic in `GetCNPJsToUpdateViaFornecedoresAPIRequester` correctly separates CPFs from CNPJs — but they do this by feeding pre-built `FornecedorToUpdate` Python objects directly into the adapter, bypassing the HTTP layer entirely.

**Requester integration tests** verify that the HTTP layer works correctly. A real HTTP call hits a mock server. The JSON is parsed for real. The tests tell you that `FornecedoresAPIRequester.get_fornecedores_to_update()` correctly deserializes a JSON array into a `list[FornecedorToUpdate]`, and that it raises `APIRequesterException` when the server returns a 500.

Both layers are valuable. But together, they leave a gap.

---

## 2. The Gap — What Neither Layer Tests

Look at this line from your unit test:

```python
# From test_get_cnpjs_to_update_via_fornecedor_api.py
@pytest.fixture
def fornecedor_to_update_with_cpf() -> FornecedorToUpdate:
    return FornecedorToUpdate(
        LOJA="test loja",
        CODIGO="test codigo",
        NOME="test nome",
        NOME_FANTASIA="test nome fantasia",
        CPF_CNPJ="529.982.247-25",   # ← you decided this format
    )
```

You decided the CPF format. You wrote `"529.982.247-25"`. The unit test passes because `CPF.create()` handles that format and `_is_cpf()` returns `True`. Good.

Now look at what the requester integration test verifies:

```python
# From test_fornecedores_api_requester.py
@pytest.fixture
def fornecedor_to_update_with_cpf_data() -> dict:
    return {
        "CPF_CNPJ": "08325475498"   # ← raw digits, no formatting
    }
```

The real API returns raw digits without formatting. The requester test verifies this parses correctly into a `FornecedorToUpdate` with `CPF_CNPJ = "08325475498"`.

**The gap:** no test verifies that `_is_cpf("08325475498")` returns `True` and that the adapter correctly excludes this fornecedor. The unit test uses `"529.982.247-25"`. The requester test uses `"08325475498"`. Neither connects the two. The adapter integration test does.

This is the gap: **you have tested each component in isolation, but not that they work correctly together with real data flowing through the full stack.**

---

## 3. The Adapter's Role — Translation

To understand why adapters deserve their own tests, you must understand what an adapter is.

In your hexagonal architecture, an adapter's job is **translation**. It translates between two different languages:

- The **external world's language**: HTTP responses, JSON shapes, API field names, status codes, the exact format of a CPF in the Fornecedores API
- The **domain's language**: `CNPJ` value objects, `Endereco` dataclasses, `CartaoCNPJ`, `Municipio`, domain exceptions like `InvalidIdentifierError`

The adapter receives something in the external language and must produce something in the domain language. If that translation is wrong, everything built on top of it is wrong — and that includes your business logic, your service layer, and ultimately the data persisted in the external system.

A translator who knows both languages perfectly can still produce a wrong translation if they mishear the original sentence. That is exactly the bug that adapter integration tests are designed to catch.

---

## 4. What Translation Bugs Look Like in Production

Translation bugs are the most dangerous class of bugs in a system like yours. Here is why: **they do not crash the system.**

A crash is obvious. An exception is logged. Someone investigates. The bug is found.

A translation bug produces wrong domain objects silently. The system keeps running. The workflow counts "successfully updated fornecedores" and reports success. But the `Fornecedor` that was updated had the wrong `tipo_pessoa`, or the wrong `endereco`, or the wrong `opt_simples_nacional` — because the adapter silently translated `null` from the API as an empty string, and your domain accepted an empty string where it expected `None`.

Consider a concrete example from your system. `GetEnderecoViaReceitaAPIRequester.get()` does this:

```python
return Endereco.create(
    endereco=response.END_LOGRADOURO,
    numero=response.END_NUMERO,
    complemento=response.END_COMPLEMENTO,
    cep=CEP.create(cep=response.END_CEP) if response.END_CEP else None,
    municipio=self._get_municipio(response.END_MUNICIPIO) if response.END_MUNICIPIO else None,
)
```

Your requester test verified that `response.END_CEP` is `None` when the API returns `null`. Your unit test for `FornecedorBuilderService` verified that when `GetEnderecoPort` returns an `Endereco` with `cep=None`, the service handles it correctly.

But neither test answers: **when the real Receita API returns `null` for `END_CEP`, does the adapter produce an `Endereco` with `cep=None`?** The conditional `if response.END_CEP` is the translation logic. It sits between the two layers you have already tested. The adapter integration test is the one that exercises it.

---

## 5. The QA Engineer's Mental Model for Adapters

A QA engineer looks at an adapter and asks three questions:

### Question 1: "What is the exact format of the input I receive from the external world?"

Not what you assumed when writing the fake. The exact format the real API returns. In your case:
- Does `CPF_CNPJ` come formatted (`"529.982.247-25"`) or raw (`"08325475498"`)?
- Does `END_CEP` come as `"57312330"` or `"57.312-330"` or `null`?
- Does `END_MUNICIPIO` come as `"ARAPIRACA"` or `"Arapiraca"` or `"ARAPIRACA - AL"`?

The answer to each of these questions is a potential source of a translation bug. The adapter integration test forces you to use the real format and verify the translation produces the correct domain object.

### Question 2: "What are all the ways the translation can go silently wrong?"

A translation fails loudly when it raises an exception. But the worst translations fail silently — they produce a domain object with a wrong value. For each field the adapter builds, ask: "what happens if this field is null? What if it's an empty string? What if it has unexpected whitespace? What if it has special characters?" Each answer that produces a different domain object is a test case.

### Question 3: "What is the contract I expose to the layer above me?"

The adapter makes a promise to its caller. `GetCNPJsToUpdateViaFornecedoresAPIRequester` promises: "call `.get()` and I will give you a `list[CNPJ]` — only valid CNPJs, no CPFs, and if anything is neither, I raise `InvalidIdentifierError`." The adapter integration test verifies this promise holds when the input comes from the real HTTP layer, not a fake.

---

## 6. How This Specifically Improves Your System's Quality

There are four concrete quality improvements that adapter integration tests bring to this specific project.

### 6.1 — Closes the Format Gap

Your unit tests control the exact format of test data. The real API controls the format in production. Adapter integration tests use a mock HTTP server to replicate the exact format the real API returns — the same format your requester integration tests already established. This closes the gap between "the unit test passed" and "production works with real data."

### 6.2 — Verifies Chained Dependencies Work Together

`GetEnderecoViaReceitaAPIRequester` depends on two things: `ReceitaAPIRequester` and `MunicipioLookupPort`. You have tested each separately. But the adapter chains them: it calls the requester, takes the municipio name from the response, and passes it to the lookup. The integration test verifies this chain: a real HTTP call returns a real municipio name, and a real second HTTP call looks it up, and the result is a correct `Endereco`. If the municipio name format differs between what the Receita API returns and what the Fornecedores API expects for lookup, neither requester test catches it — the adapter integration test does.

### 6.3 — Validates Error Translation

Each adapter has a contract about what errors it raises. `GetEnderecoViaReceitaAPIRequester` wraps lookup failures in `ErrorWhileGettingExternalDataError`. This wrapping is tested in unit tests with a fake that throws. But the adapter integration test verifies it when the HTTP call actually fails — when the mock server returns 404 for the municipio endpoint. This matters because the caller (`FornecedorBuilderService`) catches `ErrorWhileGettingExternalDataError` specifically. If the adapter propagates the raw `NotFoundError` instead, the service layer does not handle it.

### 6.4 — Protects Against Regressions from API Changes

When the external API changes — a field is renamed, a new status code is introduced, a previously non-null field starts returning null — your requester integration test will catch the parsing change, and your adapter integration test will catch whether the translation still produces the correct domain object. This double layer of protection means that when the API changes, you know exactly which layer broke and why.

---

## 7. The Testing Staircase for This System

Think of your test layers as a staircase. Each step stands on the one below it.

```
                    ┌──────────────────────────────┐
  Service tests     │  FornecedorBuilderService    │  ← full service with real adapters
                    └──────────────────────────────┘
                              stands on
                    ┌──────────────────────────────┐
  Adapter tests     │  GetEnderecoAdapter           │  ← real HTTP → real domain object
  (the new layer)   │  GetCNPJsToUpdateAdapter      │
                    │  MunicipioLookupAdapter        │
                    └──────────────────────────────┘
                              stands on
                    ┌──────────────────────────────┐
  Requester tests   │  FornecedoresAPIRequester     │  ← real HTTP → intermediate struct
                    │  ReceitaAPIRequester           │
                    └──────────────────────────────┘
                              stands on
                    ┌──────────────────────────────┐
  Unit tests        │  Domain logic, value objects  │  ← pure logic, no I/O
                    │  Services, workflows          │
                    └──────────────────────────────┘
```

Each step trusts the one below it. The adapter test trusts that the requester works correctly (verified by the requester test) and focuses only on whether the translation logic produces the right domain object. You do not re-test the HTTP parsing in the adapter test — you assume it works because you have already tested it. This is the principle of **test isolation across layers**: each layer's test focuses on that layer's responsibility, nothing more.

---

## 8. The Single Most Important Principle

Before writing a single adapter test, internalize this:

**You are not testing the adapter's code. You are testing the adapter's contract.**

The code is an implementation detail. The contract is the promise the adapter makes to the layer above it. Contracts are what callers depend on. When a contract is violated — even if the code looks correct — the system breaks.

Write every adapter test as a verification of a specific clause of that contract:
- "Given this real HTTP response shape, I will produce this domain object"
- "Given this null field in the HTTP response, I will produce this field as None in the domain object"
- "Given this failure from a dependency, I will raise this specific exception"

If a test cannot be expressed as a contract clause, it should not exist.
