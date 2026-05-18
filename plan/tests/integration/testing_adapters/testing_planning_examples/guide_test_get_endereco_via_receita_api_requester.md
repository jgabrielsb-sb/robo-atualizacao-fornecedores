# Guide: Integration Tests for `GetEnderecoViaReceitaAPIRequester`

## 1. Why This Case Is Different

Before writing a single test, understand the structural difference from `GetCNPJsToUpdateViaFornecedoresAPI`.

`GetCNPJsToUpdateViaFornecedoresAPI` has one dependency:

```python
def __init__(self, fornecedores_api_requester: FornecedoresAPIRequester):
```

It depends on a **concrete class**. There is one HTTP boundary. You wire the real requester against the mock HTTP server. Done.

`GetEnderecoViaReceitaAPIRequester` has two dependencies:

```python
def __init__(
    self,
    municipio_lookup_port: MunicipioLookupPort,   # abstract port
    receita_api_requester: ReceitaAPIRequester,    # concrete HTTP class
):
```

One dependency is concrete. One is abstract. This changes everything about how you wire the tests.

---

## 2. The Decision: What to Wire, What to Stub

### Wire the `ReceitaAPIRequester` against the mock HTTP server

This is the same reasoning as before: the real API returns raw data with a specific format. The adapter's translation logic — the `if response.END_CEP`, the `if response.END_MUNICIPIO`, the `Endereco.create()` call — must be tested against the format the real API actually returns. That format is established by the requester integration tests. The adapter integration test verifies the translation works end-to-end with that format.

**Rule: always wire concrete HTTP requesters against the mock HTTP server.**

### Stub the `MunicipioLookupPort`

`MunicipioLookupPort` is an abstract port. An abstract port is a **seam** — a deliberate cut point in the architecture where the system can be split. The adapter does not care how the municipio is looked up. It calls `.get(municipio_name)` and expects a `Municipio` back. The concrete implementation is irrelevant to the adapter's translation logic.

**Rule: always stub abstract ports in adapter integration tests.**

There are three specific reasons for this rule, and you should understand all three:

**Reason 1 — Test focus.** The adapter's responsibility is: translate a `ReceitaAPIRequester` response into an `Endereco` domain object. That is what you are testing. The `MunicipioLookupPort` is an input to that translation, not the subject of it. Stubbing it lets you control that input precisely and keep the test focused on the thing you are measuring.

**Reason 2 — Failure isolation.** If you wired the real `MunicipioLookupViaFornecedoresAPI` (which itself calls `FornecedoresAPIRequester.get_municipio_by_name()`), you would need a second mock HTTP server for the Fornecedores API. Now your test has two mock servers. When it fails, the failure could be in `GetEnderecoViaReceitaAPIRequester`, or in `MunicipioLookupViaFornecedoresAPI`, or in `FornecedoresAPIRequester`. You cannot tell. The value of a layered test suite comes from knowing exactly which layer broke. Stubbing the port restores that clarity.

**Reason 3 — Responsibility.** `MunicipioLookupViaFornecedoresAPI`'s behavior is already covered by the requester integration tests for `FornecedoresAPIRequester`. Re-testing it here adds no new information. It just makes your test slower and more fragile.

### The contrast stated plainly

| Dependency | Type | How to handle |
|---|---|---|
| `ReceitaAPIRequester` | Concrete HTTP class | Wire the real class against mock HTTP server |
| `MunicipioLookupPort` | Abstract port | Stub it — return a controlled `Municipio` |

This is the general rule for adapter integration tests in a hexagonal architecture: **wire your concrete HTTP dependencies, stub your abstract ports**.

---

## 3. The Stub

Because `MunicipioLookupPort` is an abstract class, the stub is a minimal concrete subclass:

```python
class MunicipioLookupStub(MunicipioLookupPort):
    def get(self, municipio_name: str) -> Municipio:
        return Municipio(
            nome=municipio_name,
            codigo_ibge=CodigoMunicipioIBGE(value="2704302"),
        )
```

This stub does two important things:
1. It returns a real `Municipio` domain object (not a mock). The adapter test can then assert that the `Municipio` appears correctly in the resulting `Endereco`.
2. It passes `municipio_name` through as `nome`. This means when you assert `endereco.municipio.nome == "MACEIO"`, you are asserting that the adapter correctly extracted `END_MUNICIPIO` from the HTTP response and passed it to the lookup — which is exactly the translation behavior you care about.

The stub does not validate the municipio name, does not call any HTTP endpoint, and does not raise. It is the happy path. The error path (lookup fails) is tested separately using a different stub that raises.

---

## 4. The Fixtures

### The `adapter` fixture

```python
@pytest.fixture
def adapter(httpserver: HTTPServer) -> GetEnderecoViaReceitaAPIRequester:
    municipio_lookup_stub = MunicipioLookupStub()
    requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))
    return GetEnderecoViaReceitaAPIRequester(
        municipio_lookup_port=municipio_lookup_stub,
        receita_api_requester=requester,
    )
```

This fixture lives in the test file, not in `conftest.py`, because only this test file uses it.

### The URL and CNPJ constants

```python
CNPJ_VALUE = "08626186000109"
URL = f"/receita/api/v1/empresa-receita/get-by-cnpj/{CNPJ_VALUE}"
```

These are module-level constants. They match the URL template in `ReceitaAPIRequester.get_company()`.

### The `company_data` fixture

This is the same `company_data` fixture from `test_receita_api_requester.py`. Both test files mock the same endpoint with the same response shape, so this fixture belongs in `conftest.py`.

Move it from `test_receita_api_requester.py` to `src/tests/integration/app/infra/conftest.py` when you write this file — that is the moment the second file needs it.

The fixture must include the address fields with realistic values:

```python
@pytest.fixture
def company_data() -> dict:
    return {
        ...
        "END_LOGRADOURO": "RUA DAS FLORES",
        "END_NUMERO": "123",
        "END_COMPLEMENTO": "SALA 01",
        "END_CEP": "57312330",
        "END_MUNICIPIO": "MACEIO",
        ...
    }
```

---

## 5. The Tests to Implement

### Test 1 — Returns `Endereco` with CEP and municipio when all address fields are present

```
test_should_return_endereco_with_cep_and_municipio_when_all_address_fields_are_present
```

**What it tests:** The full happy path. The Receita API returns a response where `END_CEP` and `END_MUNICIPIO` are both non-null. The adapter should produce an `Endereco` with a valid `CEP` object and a valid `Municipio` object.

**Why it matters:** This is the baseline. If this fails, everything else is irrelevant. It verifies that the adapter correctly calls `CEP.create()` with the raw CEP from the HTTP response and correctly passes `END_MUNICIPIO` to the stub.

**What to assert:**
- `isinstance(result, Endereco)`
- `result.cep.value == "57312330"` (or the normalized form — check what `CEP.create()` produces)
- `result.municipio.nome == "MACEIO"` (this proves the stub received the right name)
- `result.endereco == "RUA DAS FLORES"`
- `result.numero == "123"`

---

### Test 2 — Returns `Endereco` with `cep=None` when `END_CEP` is null

```
test_should_return_endereco_with_cep_none_when_api_returns_null_cep
```

**What it tests:** The conditional `cep=CEP.create(cep=response.END_CEP) if response.END_CEP else None`. When `END_CEP` is `None` in the HTTP response, the adapter must skip `CEP.create()` and set `cep=None`.

**Why it matters:** This is a silent translation bug waiting to happen. If you remove the `if response.END_CEP` guard, `CEP.create(cep=None)` will raise an exception — but that exception won't be caught, so it surfaces as a crash rather than a silent wrong value. This test verifies the guard is there and works. The unit test for `FornecedorBuilderService` may verify that `Endereco` with `cep=None` is handled correctly downstream, but it uses a fake. This test verifies the guard with a real HTTP `null`.

**Setup:** Use `company_data` but override `END_CEP` to `None`.

**What to assert:**
- `result.cep is None`
- `result.municipio is not None` (municipio is unaffected)

---

### Test 3 — Returns `Endereco` with `municipio=None` when `END_MUNICIPIO` is null

```
test_should_return_endereco_with_municipio_none_when_api_returns_null_municipio
```

**What it tests:** The conditional `municipio=self._get_municipio(response.END_MUNICIPIO) if response.END_MUNICIPIO else None`. When `END_MUNICIPIO` is `None`, the adapter must skip the lookup entirely and set `municipio=None`.

**Why it matters:** If the guard is missing, `_get_municipio(None)` will call `self._municipio_lookup_port.get(None)`, which the real implementation will pass to `FornecedoresAPIRequester.get_municipio_by_name(None)`. The result is unpredictable. This test verifies the guard is present and works without the lookup being called at all.

**Setup:** Use `company_data` but override `END_MUNICIPIO` to `None`.

**What to assert:**
- `result.municipio is None`
- `result.cep is not None` (CEP is unaffected)

---

### Test 4 — Returns `Endereco` with both `cep=None` and `municipio=None` when both fields are null

```
test_should_return_endereco_with_cep_and_municipio_none_when_api_returns_null_address_fields
```

**What it tests:** Both guards together. The Receita API can return a company record where the address is entirely absent.

**Why it matters:** This is a realistic case (a company registered without a complete address). Testing it separately from Tests 2 and 3 ensures the two conditions don't interfere with each other.

**Setup:** Use `company_data` with both `END_CEP` and `END_MUNICIPIO` set to `None`.

**What to assert:**
- `result.cep is None`
- `result.municipio is None`

---

### Test 5 — Raises `ErrorWhileGettingExternalDataError` when the municipio lookup fails

```
test_should_raise_error_while_getting_external_data_when_municipio_lookup_fails
```

**What it tests:** The `_get_municipio` exception wrapper:

```python
def _get_municipio(self, municipio_name: str) -> Municipio:
    try:
        return self._municipio_lookup_port.get(municipio_name)
    except Exception as e:
        raise ErrorWhileGettingExternalDataError(...) from e
```

Any exception from the lookup — `NotFoundError`, `APIRequesterException`, anything — must be wrapped in `ErrorWhileGettingExternalDataError`. The workflow layer catches this specific exception type. If the adapter propagates the raw exception instead, the workflow's error handling breaks.

**Setup:** This test needs a different stub — one that raises. You cannot use the `adapter` fixture for this test because that fixture uses the happy-path stub. Either:
- Override the fixture for this test with an inline `adapter` using a raising stub.
- Or parameterize the `adapter` fixture to accept a stub — but that adds complexity.

The simplest approach: build the adapter inline in the test body.

```python
class FailingMunicipioLookupStub(MunicipioLookupPort):
    def get(self, municipio_name: str) -> Municipio:
        raise Exception("lookup failure")

def test_should_raise_error_while_getting_external_data_when_municipio_lookup_fails(
    self, httpserver: HTTPServer, company_data: dict
):
    httpserver.expect_request(URL).respond_with_json(company_data)
    requester = ReceitaAPIRequester(base_url=httpserver.url_for(""))
    adapter = GetEnderecoViaReceitaAPIRequester(
        municipio_lookup_port=FailingMunicipioLookupStub(),
        receita_api_requester=requester,
    )
    with pytest.raises(ErrorWhileGettingExternalDataError):
        adapter.get(CNPJ.create(cnpj=CNPJ_VALUE))
```

**Why it matters:** The workflow layer catches `ErrorWhileGettingExternalDataError` specifically. If the adapter propagates the raw exception, the workflow's `except ErrorWhileGettingExternalDataError` block is never hit. The error escalates past the handler, and the behavior becomes wrong in production. This test is the contract check for that wrapping.

**What to assert:**
- `pytest.raises(ErrorWhileGettingExternalDataError)`

---

### Test 6 — Propagates `APIRequesterException` when the Receita API returns non-200

```
test_should_propagate_api_requester_exception_when_receita_api_returns_non_200
```

**What it tests:** The adapter does not catch `APIRequesterException`. It propagates up from `get_company()` untouched. The caller (the workflow) must receive `APIRequesterException` when the HTTP call fails.

**Why it matters:** The workflow layer's error handling depends on receiving the right exception type. This test is the only one that verifies `APIRequesterException` propagates correctly through the full stack — from the mock server's 500 response, through `ReceitaAPIRequester.get_company()`, through `GetEnderecoViaReceitaAPIRequester.get()`, to the caller.

**Setup:** Mock the server to return 500.

**What to assert:**
- `pytest.raises(APIRequesterException)`

---

### Test 7 — Propagates `NotFoundError` when the Receita API returns 404

```
test_should_propagate_not_found_error_when_receita_api_returns_404
```

**What it tests:** Same reasoning as Test 6, but for the 404 case. The Receita API returns 404 when there is no company with the requested CNPJ. `ReceitaAPIRequester.get_company()` raises `NotFoundError`. The adapter does not catch it. The caller receives `NotFoundError`.

**Why it matters:** The workflow layer may handle `NotFoundError` differently than `APIRequesterException` — for example, by logging "company not found" and skipping, rather than by failing the entire run. If the adapter accidentally swallows `NotFoundError` (or wraps it in something else), the workflow's special handling never triggers.

**What to assert:**
- `pytest.raises(NotFoundError)`

---

## 6. The Difference Table

| Scenario | Unit test | Integration test |
|---|---|---|
| Full address, all fields | Fake endereco returned by port | Real HTTP response → real `Endereco` |
| `END_CEP` is null | Built directly into fixture | Real HTTP `null` → `cep=None` verified |
| `END_MUNICIPIO` is null | Built directly into fixture | Real HTTP `null` → lookup skipped, `municipio=None` |
| Both fields null | May not exist as explicit test | Real HTTP `null` for both simultaneously |
| Lookup failure | Fake port raises | Stub raises → `ErrorWhileGettingExternalDataError` |
| Receita API 500 | Not testable with fakes | Mock server 500 → `APIRequesterException` |
| Receita API 404 | Not testable with fakes | Mock server 404 → `NotFoundError` |

---

## 7. The Structural Rule to Carry Forward

This adapter exposed a general rule for hexagonal architecture:

> **Wire concrete HTTP dependencies. Stub abstract ports.**

A port abstraction (`MunicipioLookupPort`) is a seam. Seams exist so you can cut the system and test each side independently. In an adapter integration test, you cut at every port boundary. You do not wire the port's concrete implementation — that implementation has its own tests. You wire only what is unique to this adapter: its HTTP dependency and its translation logic.

When you encounter a future adapter that has N dependencies, ask for each one:
- Is this a concrete HTTP class? Wire it against the mock HTTP server.
- Is this an abstract port? Stub it with a minimal inline implementation that returns controlled values.

The adapter integration test is complete when it covers:
1. The full translation happy path with real HTTP format.
2. Every conditional in the translation logic (each `if field else None`).
3. Each error the adapter wraps (tested with a raising stub).
4. Each exception the adapter propagates (tested with a non-200 mock server response).
