# Integration Tests Guide

## 1. What Are Integration Tests and Why Do They Differ from Your Unit Tests

Your unit tests are excellent at testing **logic in isolation**. They verify that the workflow counts failures correctly, that the builder service picks the right address source, that value objects validate inputs. But they do this by substituting fakes at every port boundary — no real HTTP call, no real queue, no real parsing of an external payload.

The gap they leave is the **translation layer**: code that speaks JSON over HTTP to a server, parses the response, and turns it into your domain objects. If that layer has a bug — wrong field name, wrong status-code handling, wrong type coercion — your unit tests never catch it because they never exercise it.

Integration tests close that gap. They test one adapter against a **real but controlled** dependency: a real HTTP server (running in-process, locally), a real RabbitMQ broker, etc.

### The boundary difference, visualized

```
UNIT TEST:
  Workflow → [FakeGetCNPJs]                ← no HTTP, no parsing
  Workflow → [FakeBuildFornecedor]
  Workflow → [FakeFornecedorRepository]

INTEGRATION TEST:
  GetCNPJsToUpdateAdapter → FornecedoresAPIRequester → [real local HTTP server]
  GetEnderecoAdapter      → ReceitaAPIRequester      → [real local HTTP server]
  FornecedoresAPIRequester                           → [real local HTTP server]
```

You control the HTTP server: you define exactly what JSON it returns, what status code, what headers. The adapter must parse it correctly or the test fails. That is the thing you are testing.

---

## 2. Setup

### 2.1 Add the test dependency

Add `pytest-httpserver` to your `pyproject.toml` dev dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-html>=3.0.0",
    "pytest-httpserver>=1.0.0",   # ← add this
]
```

Install: `pip install pytest-httpserver`

`pytest-httpserver` spins up a real `werkzeug` HTTP server in-process. Your adapter makes a real `requests.get()` call to it. No monkey-patching, no mock objects — real TCP, real HTTP, real JSON parsing.

### 2.2 Folder structure

Mirror your `tests/unit/` tree inside a new `tests/integration/` directory:

```
src/tests/
├── unit/
│   └── app/
│       ├── application/...
│       ├── domain/...
│       └── infra/...
└── integration/                         ← new
    ├── __init__.py
    └── app/
        ├── __init__.py
        ├── infra/
        │   ├── __init__.py
        │   ├── api_requester/
        │   │   ├── __init__.py
        │   │   ├── test_fornecedores_api_requester.py
        │   │   └── test_receita_api_requester.py
        │   └── adapters/
        │       ├── __init__.py
        │       ├── get_cnpjs_to_update/
        │       │   ├── __init__.py
        │       │   └── test_get_cnpjs_to_update_via_fornecedor_api.py
        │       ├── get_endereco/
        │       │   ├── __init__.py
        │       │   └── test_get_endereco_via_receita_api.py
        │       └── municipio_lookup/
        │           ├── __init__.py
        │           └── test_municipio_lookup_via_fornecedores_api.py
        └── application/
            ├── __init__.py
            └── services/
                ├── __init__.py
                └── test_fornecedor_builder_service.py
```

### 2.3 pytest marker

You already declared `integration_tests` in `pyproject.toml`. Tag every integration test with it:

```python
@pytest.mark.integration_tests
def test_something(httpserver):
    ...
```

Run only integration tests: `pytest -m integration_tests`  
Run only unit tests: `pytest -m "not integration_tests"`

### 2.4 The `httpserver` fixture

`pytest-httpserver` provides a `httpserver` fixture automatically. It gives you a server that is fresh per test. Basic usage pattern:

```python
from pytest_httpserver import HTTPServer

def test_something(httpserver: HTTPServer):
    # Define what the server returns for a given route
    httpserver.expect_request("/some/path").respond_with_json({"key": "value"})

    # Point your real requester at the local server
    url = httpserver.url_for("")   # e.g. "http://localhost:PORT"
    requester = FornecedoresAPIRequester(base_url=url)

    result = requester.get_fornecedores_to_update()
    assert result[0].nome == "..."
```

The server raises `AssertionError` at test teardown if an expected request was never called — which catches bugs where your adapter never makes the HTTP call at all.

---

## 3. Group 1: API Requester Tests

These are the lowest-level integration tests. They test the `FornecedoresAPIRequester` and `ReceitaAPIRequester` directly — the classes that own the HTTP calls.

**Why test these separately?** Your unit tests for the adapters mock these requesters at the Python class level (e.g. `FakeFornecedoresAPIRequester`). If the real requester has a bug in how it parses the JSON, calls the wrong URL, or mishandles a status code, those unit tests never catch it.

### 3.1 `FornecedoresAPIRequester`

File: `tests/integration/app/infra/api_requester/test_fornecedores_api_requester.py`

#### `get_fornecedores_to_update()`

| Test | What you assert |
|---|---|
| Returns list of `FornecedorToUpdate` on 200 | Each field (`loja`, `codigo`, `nome`, `nome_fantasia`, `cpf_cnpj`) is parsed correctly |
| Returns empty list when API returns `[]` | Result is an empty list, not `None` |
| Raises `APIRequesterException` on non-200 | Exception is raised; no partial result is returned |

**Critical cases to test:**
- A response where `cpf_cnpj` contains a raw CPF string like `"529.982.247-25"` — the requester must return it as-is (parsing is the adapter's job, not the requester's).
- A response where `cpf_cnpj` is a formatted CNPJ like `"62.173.620/0001-80"` — same thing, pass through.

#### `get_municipio_by_name()`

| Test | What you assert |
|---|---|
| Returns `Municipio` on 200 | `nome` and `codigo_ibge` match what the API returned |
| Raises `NotFoundError` on 404 with `"detail"` not containing `"Not Found"` | `NotFoundError` is raised |
| Raises `RouteNotFoundError` on 404 with `"detail": "Not Found"` | `RouteNotFoundError` is raised |
| Raises `APIRequesterException` on 500 | `APIRequesterException` is raised |

**Why the two 404 variants matter:** Your requester distinguishes between "the municipio was not found" and "the route itself doesn't exist" based on the response body. This is fragile logic that absolutely needs an integration test — a unit test can't catch a typo in `"Not Found"`.

### 3.2 `ReceitaAPIRequester`

File: `tests/integration/app/infra/api_requester/test_receita_api_requester.py`

#### `get_company()`

| Test | What you assert |
|---|---|
| Returns `ReceitaAPIGetCompanyResponse` on 200 with all fields | All optional fields are populated correctly |
| Returns `ReceitaAPIGetCompanyResponse` on 200 with `null` fields | Optional fields are `None`, not missing from the model |
| Raises `NotFoundError` on 404 without `"Not Found"` in detail | `NotFoundError` is raised |
| Raises `RouteNotFoundError` on 404 with `"detail": "Not Found"` | `RouteNotFoundError` is raised |
| Raises `UnexpectedError` on 500 | `UnexpectedError` is raised |

**Critical cases to test:** The response has ~25 optional fields. Verify that a response with all `null` values deserializes to a model where every field is `None` — not a validation error.

---

## 4. Group 2: Adapter Integration Tests

These test a full adapter — which combines the requester and business logic — against the mock HTTP server. They are one level above the requester tests.

### 4.1 `GetCNPJsToUpdateViaFornecedoresAPIRequester`

File: `tests/integration/app/infra/adapters/get_cnpjs_to_update/test_get_cnpjs_to_update_via_fornecedor_api.py`

**What your existing unit test already covers:** The filtering logic (CPF vs CNPJ, invalid identifiers). It does this by mocking `FornecedoresAPIRequester` directly.

**What the integration test adds:** It exercises the full stack — real HTTP call → real JSON parsing by `FornecedoresAPIRequester` → filtering logic. The two key questions are:

1. Does the adapter correctly parse and filter when the CNPJs/CPFs come formatted (with dots, slashes, dashes) from the real API?
2. Does it survive edge-case HTTP responses?

| Test | What you assert |
|---|---|
| Returns only CNPJs when API response contains a mix of formatted CPFs and formatted CNPJs | CPFs are filtered out; CNPJs are returned as `CNPJ` value objects |
| Returns empty list when API returns `[]` | Empty list, no exception |
| Raises `InvalidIdentifierError` when API returns an identifier that is neither valid CPF nor valid CNPJ | Exception propagates correctly |
| Raises exception when API returns non-200 | Exception propagates from the requester |

**Key data to use in this test:** Use formatted identifiers as they would actually appear in the real API response — `"62.173.620/0001-80"` and `"529.982.247-25"` — not raw digits. This tests that your `CNPJ.create()` and `CPF.create()` handle real-world formatted strings.

### 4.2 `MunicipioLookupViaFornecedoresAPI`

File: `tests/integration/app/infra/adapters/municipio_lookup/test_municipio_lookup_via_fornecedores_api.py`

| Test | What you assert |
|---|---|
| Returns `Municipio` with correct `nome` and `codigo_ibge` on 200 | `Municipio` fields match what the server returned |
| Raises error when municipio is not found (404) | Error propagates from the requester |

This adapter is a thin wrapper — the tests are simple but important because `MunicipioLookupPort` is used by both `CartaoCNPJBuilder` and `GetEnderecoViaReceitaAPIRequester`.

### 4.3 `GetEnderecoViaReceitaAPIRequester`

File: `tests/integration/app/infra/adapters/get_endereco/test_get_endereco_via_receita_api.py`

This adapter talks to two dependencies: `ReceitaAPIRequester` (HTTP) and `MunicipioLookupPort`. In an integration test, you use a **real** `ReceitaAPIRequester` with a mock HTTP server, but you can keep a fake `MunicipioLookupPort` unless you want to test the municipio lookup path too (which is covered in 4.2).

| Test | What you assert |
|---|---|
| Returns full `Endereco` when API provides all address fields | All `Endereco` fields match the server response |
| Returns `Endereco` with `municipio=None` when `END_MUNICIPIO` is null in the response | `municipio` is `None`, no exception |
| Returns `Endereco` with `cep=None` when `END_CEP` is null in the response | `cep` is `None`, no exception |
| Propagates error from `MunicipioLookupPort` when municipio lookup fails | Exception is raised and is of the correct type (`ErrorWhileGettingExternalDataError`) |

**Key insight:** The Receita API response has many optional fields. Test the fully-populated case AND the minimal case (only nulls) to ensure your `Endereco.create()` handles `None` gracefully for every field.

---

## 5. Group 3: Service Integration Tests — `FornecedorBuilderService`

File: `tests/integration/app/application/services/test_fornecedor_builder_service.py`

Your unit tests for `FornecedorBuilderService` verify the business logic: when does it call `GetEnderecoPort`? How does it merge addresses? This is all done with fakes.

The integration test wires in the **real HTTP adapters** for `GetCartaoCNPJPort` and `GetEnderecoPort`, leaving only the Selenium adapter faked (because it hits an external government website — you cannot and should not use it in automated tests).

```
FornecedorBuilderService
  ├── GetOptSimplesNacionalPort  → FAKE (always returns True or False)
  ├── GetCartaoCNPJPort          → CartaoCNPJBuilder + [mock queue or fake]
  └── GetEnderecoPort            → GetEnderecoViaReceitaAPIRequester → [mock HTTP server]
                                         └── MunicipioLookupViaFornecedoresAPI → [mock HTTP server]
```

**Note on `GetCartaoCNPJPort`:** The real implementation uses RabbitMQ. For this group of tests, use a fake `GetCartaoCNPJPort` that returns a pre-built `CartaoCNPJ` using your existing `element_data` fixtures from the unit tests. The goal here is to test the service's interaction with the real `GetEnderecoPort` stack — not RabbitMQ.

| Test | What you assert |
|---|---|
| Builds a complete `Fornecedor` when `CartaoCNPJ` has a full address | `GetEnderecoPort` is NOT called (you can verify with a spy or counter) |
| Builds a `Fornecedor` with merged address when `CartaoCNPJ` has partial address | Fields from the Receita API fill in the missing values |
| Raises `GetCartaoCNPJError` when `GetCartaoCNPJPort` fails | Exception propagates with correct type |
| Raises `GetOptanteSimplesNacionalError` when Selenium adapter fails | Exception propagates with correct type |
| Correctly determines `tipo_pessoa=CI` for commerce/industry activity | `dados_cadastrais.tipo_pessoa` is `TipoPessoaEnum.CI` |
| Correctly determines `tipo_pessoa=OS` for other activities | `dados_cadastrais.tipo_pessoa` is `TipoPessoaEnum.OS` |
| Correctly identifies cooperativa from `natureza_juridica` | `dados_cadastrais.cooperativa` is `True` and `codigo_retencao` is `"3280"` |

**What these tests prove that unit tests cannot:** The `_get_endereco` merging logic interacts correctly with a real endpoint that returns `null` for some fields. The unit test fakes always return a complete `Endereco`. A real endpoint might return `null` for `END_COMPLEMENTO` — does your merge code handle that correctly without crashing?

---

## 6. Priority Order

Implement the tests in this order. Each group builds on the one before it.

```
1. FornecedoresAPIRequester tests         ← HTTP parsing baseline
2. ReceitaAPIRequester tests              ← HTTP parsing baseline
3. MunicipioLookupViaFornecedoresAPI      ← thin adapter, easy
4. GetCNPJsToUpdateViaFornecedoresAPI     ← depends on (1)
5. GetEnderecoViaReceitaAPIRequester      ← depends on (2) and (3)
6. FornecedorBuilderService               ← depends on (4) and (5)
```

---

## 7. Patterns to Follow Throughout

### Use `httpserver.expect_request()`, not `httpserver.expect_ordered_request()`

Unless you need to test that requests happen in a specific order, use `expect_request`. It matches any call to that path regardless of order.

### Assert on domain objects, not on raw dicts

Integration tests should assert on the same domain types your unit tests use:

```python
# Good
assert result[0] == CNPJ("62173620000180")

# Avoid — tests HTTP parsing but not domain construction
assert result[0] == "62173620000180"
```

### One server per test function, fresh state

`pytest-httpserver` gives you a fresh server per test by default (the `httpserver` fixture is function-scoped). Do not share state between tests.

### Test the errors your adapters are supposed to raise

Every `except` block in your adapters is a contract: "when the external system fails in this way, I raise this exception." Test it. Your callers depend on those specific exception types.

```python
# In GetEnderecoViaReceitaAPIRequester:
#   except Exception as e:
#       raise ErrorWhileGettingExternalDataError(...) from e
#
# Test: make the mock server return 500 → assert ErrorWhileGettingExternalDataError is raised

def test_raises_correct_error_when_municipio_lookup_fails(httpserver):
    httpserver.expect_request("/api/v1/municipios/name/MACEIO").respond_with_data(
        "Internal Server Error", status=500
    )
    ...
    with pytest.raises(ErrorWhileGettingExternalDataError):
        adapter.get(cnpj)
```

### Use `conftest.py` for shared fixtures

Put shared HTTP response payloads in a `conftest.py` at the `tests/integration/` level, or in a `fixtures/` module. Reuse your existing data from `test_cartao_cnpj_builder.py` — those queue response dicts are the canonical shape of what `GetCartaoCNPJViaQueueRequester` returns, and they are perfect as test data.

---

## 8. What Integration Tests Do NOT Replace

- **Unit tests for business logic** — keep them. The `FornecedorBuilderService` merging logic, the `GetAndUpdateFornecedoresWorkflow` counting logic: these are best verified in isolation because you can construct exact scenarios (what if 2 of 5 fail at build, and 1 of the remaining 3 fails at update?). Integration tests are expensive to set up for every edge case.
- **Value object validation tests** — keep them. `CNPJ`, `CPF`, `CEP`, etc. These have no infrastructure dependency and unit tests cover them perfectly.

---

## 9. What Comes After Integration Tests

Once the integration test suite is stable, the next layer is a **full system test** of `GetAndUpdateFornecedoresWorkflow.run()` with all real adapters wired in:

- Mock HTTP server for Fornecedores API and Receita API
- Fake `GetOptSimplesNacionalPort` (Selenium stays out)
- Real `CartaoCNPJBuilder` fed with controlled queue responses via a fake `GetCartaoCNPJPort`

This gives you end-to-end confidence that the workflow correctly drives all layers from CNPJ list retrieval through final update, without touching the government website or a live queue.
