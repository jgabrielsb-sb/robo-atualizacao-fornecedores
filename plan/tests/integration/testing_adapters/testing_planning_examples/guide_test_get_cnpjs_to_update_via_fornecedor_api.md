# Guide: Integration Tests for `GetCNPJsToUpdateViaFornecedoresAPIRequester`

## 1. The Question These Tests Answer

Your unit tests already answer: **"does the filtering logic work with data I invented?"**

The integration tests answer a different question: **"does the filtering logic work with data the real API actually produces?"**

These are not the same question. The unit tests feed pre-built `FornecedorToUpdate` objects directly into the adapter — no HTTP call, no JSON parsing, no real format constraints. The integration tests feed a raw JSON response through a real HTTP call, let the requester parse it into `FornecedorToUpdate`, and only then hand it to the adapter's filtering logic. The full stack runs.

The fact that both questions need an answer is proven by the data. Look at what your unit tests use:

```python
CPF_CNPJ="529.982.247-25"   # formatted with dots and dash — you invented this
CPF_CNPJ="62.173.620/0001-80"  # formatted — you invented this too
```

And what your requester integration tests proved the real API actually returns:

```python
"CPF_CNPJ": "08325475498"    # raw 11 digits — no formatting at all
"CPF_CNPJ": "08626186000109" # raw 14 digits — no formatting at all
```

No existing test runs `_is_cpf("08325475498")` or `CNPJ.create(cnpj="08626186000109")`. In this specific case both happen to work because `CPF.create()` and `CNPJ.create()` strip non-digits before validating. But "happens to work" and "is tested to work" are different things. The integration test turns the assumption into a verified fact.

---

## 2. How the Structure Differs from the Unit Tests

### The unit test structure

```python
# Build a FornecedorToUpdate Python object directly — no HTTP
fornecedor = FornecedorToUpdate(CPF_CNPJ="529.982.247-25", ...)

# Wire a fake requester that returns the object
fake_requester = FakeFornecedoresAPIRequester([fornecedor])

# Instantiate the adapter with the fake
adapter = GetCNPJsToUpdateViaFornecedoresAPIRequester(fornecedores_api_requester=fake_requester)

# Call the method
result = adapter.get()
```

The fake short-circuits the HTTP layer entirely. `FornecedorToUpdate` objects arrive at the adapter already built.

### The integration test structure

```python
# Tell the mock HTTP server what to return as raw JSON
httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json([
    {"LOJA": "01", ..., "CPF_CNPJ": "08325475498"},
])

# Wire the REAL requester pointing at the mock server
requester = FornecedoresAPIRequester(base_url=httpserver.url_for(""))

# Wire the REAL adapter with the REAL requester
adapter = GetCNPJsToUpdateViaFornecedoresAPIRequester(fornecedores_api_requester=requester)

# Call the method
result = adapter.get()
```

The JSON is parsed for real. `FornecedorToUpdate` is deserialized for real. The filtering logic runs against the deserialized object. Three real operations happen instead of one.

### The `adapter` fixture

Because every integration test in this file repeats the same two-line wiring, extract it into a fixture:

```python
@pytest.fixture
def adapter(httpserver: HTTPServer) -> GetCNPJsToUpdateViaFornecedoresAPIRequester:
    requester = FornecedoresAPIRequester(base_url=httpserver.url_for(""))
    return GetCNPJsToUpdateViaFornecedoresAPIRequester(fornecedores_api_requester=requester)
```

This fixture lives in the test file — not in `conftest.py` — because only this test file uses it. Each test then receives `adapter` as a parameter and focuses entirely on what varies: the mock server response and the assertion.

### The response data fixtures

`fornecedor_to_update_with_cpf_data` and `fornecedor_to_update_with_cnpj_data` come from `conftest.py` at `src/tests/integration/app/infra/conftest.py`. They are automatically available — no import needed. These are the same fixtures the requester tests use, which is precisely the point: the adapter test mocks the same HTTP endpoint with the same response shape.

---

## 3. The Tests to Implement

### Test 1 — Returns only CNPJs when the API response contains a mix

```
test_should_return_only_cnpjs_when_api_returns_mix_of_cpfs_and_cnpjs
```

**What it does:** Mock the endpoint to return one fornecedor with a raw CPF and one with a raw CNPJ. Assert the result contains exactly one `CNPJ` domain object with the right value.

**How it differs from the unit test:** The unit test (`test_should_return_just_cnpjs_when_some_fornecedores_have_cpfs`) feeds formatted strings (`"529.982.247-25"`, `"62.173.620/0001-80"`). This test feeds raw digits (`"08325475498"`, `"08626186000109"`) — the format the real API actually returns. It verifies that `_is_cpf()` and `CNPJ.create()` handle raw-digit strings from a real HTTP response correctly.

**What to assert:**
- `len(result) == 1`
- `isinstance(result[0], CNPJ)`
- `result[0].value == "08626186000109"`

---

### Test 2 — Returns empty list when all identifiers are CPFs

```
test_should_return_empty_list_when_api_returns_only_cpfs
```

**What it does:** Mock the endpoint to return two fornecedores both with raw CPF values. Assert the result is `[]`.

**How it differs from the unit test:** The unit test (`test_should_return_empty_list_when_all_fornecedores_have_cpfs`) feeds formatted CPFs through a fake. This test runs the full stack: the mock server returns raw CPF digits → real HTTP parsing → real `_is_cpf()` call → empty result. It verifies that `_is_cpf("08325475498")` — with a real unformatted CPF — returns `True` and the fornecedor is correctly skipped.

**What to assert:**
- `result == []`

---

### Test 3 — Returns empty list when the API returns an empty array

```
test_should_return_empty_list_when_api_returns_empty_array
```

**What it does:** Mock the endpoint to return `[]`. Assert the result is `[]`.

**How it differs from the unit test:** The unit test (`test_should_raise_empty_list_when_there_are_no_fornecedores_to_update`) tests both `None` and `[]` return values from a fake requester. This test verifies the specific case where the HTTP endpoint returns an empty JSON array — a realistic API state — and that the `or []` fallback in `self._fornecedores_api_requester.get_fornecedores_to_update() or []` produces the right result.

**What to assert:**
- `result == []`

---

### Test 4 — Raises `InvalidIdentifierError` when the API returns an unrecognised identifier

```
test_should_raise_invalid_identifier_error_when_api_returns_identifier_that_is_neither_cpf_nor_cnpj
```

**What it does:** Mock the endpoint to return a fornecedor whose `CPF_CNPJ` is a string that is neither a valid CPF length nor a valid CNPJ length — for example `"123456789"` (9 digits). Assert that `InvalidIdentifierError` is raised and that the unrecognised value appears in the exception message.

**How it differs from the unit test:** The unit test (`test_should_raise_error_when_fornecedor_has_identifier_that_is_not_a_cpf_or_cnpj`) uses `"123"` (3 digits) built directly into a `FornecedorToUpdate`. This test sends an invalid identifier through the real HTTP layer and verifies the exception surfaces correctly after full deserialization. It also uses a more realistic invalid value — a 9-digit string — that is closer to what a data quality issue in the real API might produce.

**What to assert:**
- `pytest.raises(InvalidIdentifierError)`
- The invalid identifier value appears in the exception message

---

### Test 5 — Propagates `APIRequesterException` when the API returns non-200

```
test_should_propagate_api_requester_exception_when_api_returns_non_200
```

**What it does:** Mock the endpoint to return a 500 with a JSON error body. Assert that `APIRequesterException` is raised.

**How it differs from the unit test:** **This scenario has zero coverage in the unit tests.** The fake requester never raises — it only returns a list or `None`. This means no existing test verifies what happens when `get_fornecedores_to_update()` throws. The adapter code is:

```python
fornecedores_to_update = self._fornecedores_api_requester.get_fornecedores_to_update() or []
```

The `or []` only handles `None` — it does not catch exceptions. If the requester raises `APIRequesterException`, it propagates unhandled. The workflow above catches it and wraps it in `GetCNPJsToUpdateWorkflowError`. For that wrapping to work, the exception type must be correct. This test is the only one that verifies the propagation happens with the right type.

**What to assert:**
- `pytest.raises(APIRequesterException)`

---

## 4. The Difference Table

| Scenario | Unit test | Integration test |
|---|---|---|
| Mix of CPFs and CNPJs | Formatted strings, fake requester | Raw digits, real HTTP call |
| Only CPFs | Formatted strings, fake requester | Raw digits, real HTTP call |
| Empty response | Fake returns `[]` or `None` | Mock server returns `[]` JSON |
| Invalid identifier | `"123"`, fake requester | 9-digit string, real HTTP call |
| API failure (non-200) | **Not tested** | Mock server returns 500 |

The last row is the most important. The integration test suite does not just verify the same things with different tooling — it also covers a failure path that is completely absent from the unit test suite.

---

## 5. The Rule to Carry Forward

When you sit down to write adapter integration tests, ask this about each unit test you already have:

> "Does this unit test use data I invented, or data the real system produces?"

If the answer is "data I invented," there is a corresponding integration test to write that uses the real format. If the unit test covers a failure path by making a fake raise an exception, ask whether a real dependency could fail in that way — and if so, write the integration test that makes it fail for real.

The integration test suite for an adapter is complete when:
1. Every scenario that uses invented data has a counterpart that uses real data.
2. Every failure path is covered, including ones the unit tests could not reach because fakes never raise.
