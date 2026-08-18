# Integration Tests: API Requesters

## 1. The QA Mindset — How to Think Before Writing a Single Line of Test

A QA engineer does not sit down and ask *"what should I test?"* That question leads to test lists written from memory and inevitably misses the things that actually break in production.

The right question is: **"What can go wrong here, how bad is it if it does, and what is the test that would have caught it?"**

That question has three parts. Let's look at each one.

### 1.1 What can go wrong?

Every piece of code has **assumptions baked in**. The job of a test is to make those assumptions explicit and verify they hold. For HTTP clients, the assumptions are:

- The server is at the URL I constructed.
- The server returns a JSON body with this exact shape.
- The server returns this status code in this situation.
- The field I'm reading exists and has this type.

Any one of those assumptions can fail — because of a change in the external API, a typo in your URL template, a field name mismatch between the API documentation and the real response, or a status code the API sends that you didn't handle.

### 1.2 How bad is it?

Not all failures are equal. A QA engineer thinks in terms of **risk**, which is the product of two things:

- **Impact**: how bad is the outcome if this breaks? (Does the whole robot stop? Does data get corrupted? Does the error get silently swallowed?)
- **Detectability**: how quickly will you know it broke? (Is there an exception that surfaces immediately, or does it silently return wrong data?)

Silent failures are the worst. An exception that propagates immediately is almost self-documenting — you see the error and know where to look. But a method that returns wrong data without raising anything can corrupt your database for hours before anyone notices.

### 1.3 What is the test that would have caught it?

This is where you move from analysis to action. For every risk you identified, you write the smallest test that would detect it. That test should:

- Fail when the bug is present.
- Pass when the bug is fixed.
- Say nothing about anything else.

A test that checks ten things at once tells you something is broken but not what. A focused test tells you exactly what assumption failed.

---

## 2. Why Start with the API Requesters?

Your system has two HTTP API requesters:

- `FornecedoresAPIRequester` — talks to the Fornecedores API
- `ReceitaAPIRequester` — talks to the Receita API

These are the **translation layer** between your Python domain and the external world. They are responsible for:

1. Building the correct URL
2. Making the HTTP call
3. Reading the response status code
4. Parsing the JSON body into a Python structure
5. Raising the right exception for each failure mode

Your existing unit tests **never test this layer**. Look at what happens in `test_get_cnpjs_to_update_via_fornecedor_api.py`:

```python
class FakeFornecedoresAPIRequester(FornecedoresAPIRequester):
    def get_fornecedores_to_update(self) -> list[FornecedorToUpdate] | None:
        return self._mock_get_fornecedores_to_update  # ← returns Python objects directly
```

The fake bypasses steps 1 through 5 entirely. It never makes an HTTP call, never reads JSON, never touches the status code. The adapter's business logic (filter CPFs from CNPJs) is tested, but the requester's job (speak HTTP correctly) is invisible to the test suite.

The gap is: **if the real API returns `"cpf_cnpj"` as `"cpfCnpj"` (camelCase), or if the status code for a missing record changes from 404 to 422, your unit tests would still pass while production silently breaks.**

Integration tests close this gap by using a real HTTP server. The `requests.get()` call happens for real, the JSON is parsed for real, and your domain objects are constructed from that parse — just as they would be in production.

### Why the requesters before the adapters?

The adapters depend on the requesters. If you write adapter integration tests but the requester has a bug, your adapter test will fail and you won't know whether the bug is in the requester or the adapter. Testing the requesters first gives you a stable foundation. When an adapter test fails, you can be confident the requester layer works and look at the adapter logic instead.

This is the same principle that makes unit testing valuable: isolate, verify, then build up.

---

## 3. Understanding What You Are Testing — The Contract

Before writing a test, you must know what you are testing against. The concept is called a **contract**: a formal description of what a function promises.

Every function has three parts to its contract:

- **Input**: what it accepts
- **Output**: what it guarantees to return when things go well
- **Exceptions**: exactly which exception it raises and when

If any part of the contract is violated — by a bug, a refactor, or an API change — a test for that part should fail.

Let's read the contracts from the actual code.

### 3.1 `FornecedoresAPIRequester.get_fornecedores_to_update()`

```python
def get_fornecedores_to_update(self) -> list[FornecedorToUpdate] | None:
    url = f"{self._base_url}/api/v1/fornecedores-to-update"
    response = requests.get(url)
    data = response.json()          # ← called BEFORE checking status code
    status_code = response.status_code

    if status_code == HTTPStatus.OK:
        return [FornecedorToUpdate(**fornecedor) for fornecedor in data]
    else:
        raise APIRequesterException(...)
```

**Contract:**
- Input: none (uses `base_url` from constructor)
- Output: `list[FornecedorToUpdate]` on HTTP 200
- Exceptions: `APIRequesterException` on any non-200 status

**Hidden assumption to examine:** `data = response.json()` is called before the status check. If the server returns a 500 with an HTML error page (which many servers do), `response.json()` raises a `JSONDecodeError` before you reach the `else` branch. Your callers expect `APIRequesterException`, not `JSONDecodeError`. This is a bug that only an integration test can reveal — your unit tests never make a real HTTP call, so they never hit this.

**Another assumption:** `FornecedorToUpdate(**fornecedor)` uses `**` unpacking. Pydantic v2 will silently ignore extra fields. But if the API response uses a different field name — say, `"cpfCnpj"` instead of `"cpf_cnpj"` — Pydantic will raise a `ValidationError`, not `APIRequesterException`. Your callers are not prepared for that.

### 3.2 `FornecedoresAPIRequester.get_municipio_by_name()`

```python
def get_municipio_by_name(self, municipio_name: str) -> Municipio:
    url = f"{self._base_url}/api/v1/municipios/name/{municipio_name}"
    response = requests.get(url)
    data = response.json()          # ← same pattern: called before status check
    status_code = response.status_code

    if status_code == HTTPStatus.OK:
        return Municipio(
            nome=municipio_name,
            codigo_ibge=CodigoMunicipioIBGE.create(ibge_code=data["codigo_ibge"]),
        )
    elif status_code == HTTPStatus.NOT_FOUND:
        raise NotFoundError(...)
    else:
        raise APIRequesterException(...)
```

**Contract:**
- Input: `municipio_name: str`
- Output: `Municipio` with the name you passed and the `codigo_ibge` from the response body
- Exceptions: `NotFoundError` on 404, `APIRequesterException` on other non-200 statuses

**Hidden assumption:** `data["codigo_ibge"]` — the key must exist with this exact name. If the API returns `"codigoIbge"` or `"ibge_code"`, this raises a raw `KeyError`, not an `APIRequesterException`. An integration test will tell you.

**Another assumption:** `CodigoMunicipioIBGE.create(ibge_code=data["codigo_ibge"])` validates that the IBGE code has exactly 7 digits. If the API ever returns a code with a different length, you get `InvalidCodigoMunicipioIBGECodeLengthError`, not `APIRequesterException`. This is an implicit dependency between the requester and the domain value object that your unit tests don't capture.

### 3.3 `ReceitaAPIRequester.get_company()`

```python
def get_company(self, cnpj: CNPJ) -> ReceitaAPIGetCompanyResponse:
    url = f"{self._base_url}/receita/api/v1/empresa-receita/get-by-cnpj/{cnpj.value}"
    response = requests.get(url)

    if response.status_code == HTTPStatus.OK:
        data = response.json()
        return ReceitaAPIGetCompanyResponse.model_validate(data)

    elif response.status_code == HTTPStatus.NOT_FOUND:
        if response.json().get("detail") and "Not Found" in response.json().get("detail"):
            raise RouteNotFoundError(...)
        raise NotFoundError(...)

    else:
        raise UnexpectedError(...)
```

**Contract:**
- Input: `cnpj: CNPJ`
- Output: `ReceitaAPIGetCompanyResponse` on HTTP 200
- Exceptions:
  - `RouteNotFoundError` on 404 when `response.json()["detail"]` contains the string `"Not Found"`
  - `NotFoundError` on 404 in all other cases
  - `UnexpectedError` on any other non-200 status

**This requester is better-structured than the other two:** it only calls `response.json()` inside each branch, not at the top. However, it calls `response.json()` twice in the 404 branch — two JSON parse calls on the same response body. This is harmless but wasteful.

**A subtle contract detail:** The condition `"Not Found" in response.json().get("detail")` is a substring match, not an equality check. This means a response with `"detail": "Company Not Found"` would match — because `"Not Found"` is a substring of `"Company Not Found"` — and raise `RouteNotFoundError` instead of `NotFoundError`. Whether this is correct depends on what your API actually returns. An integration test forces you to pin down the exact response shape and verify the right exception is raised.

**The 25 optional fields:** `ReceitaAPIGetCompanyResponse` has 25 fields, all optional. The test must verify that a response where all fields are `null` deserializes without raising a `ValidationError`. Pydantic is generally good at this, but it's an assumption worth verifying.

---

## 4. Priority Order — What to Test First and Why

A QA engineer does not test randomly. Priority is determined by the answer to: **"If this test did not exist and there was a bug here, how quickly would I know, and how bad would the damage be?"**

Use this framework:

```
Priority = Impact × (1 - Detectability)
```

High impact + hard to detect = test it first.
Low impact + easy to detect = test it last or skip it.

### Priority 1 — `get_fornecedores_to_update()` happy path

**Why first:** This is the entry point of the entire robot. Every execution starts here. If this method fails to parse the API response correctly, zero fornecedores get updated — the robot does nothing without any visible error (the workflow would receive an empty list and silently finish). It runs every time the robot runs.

**What to test:** Point a real `FornecedoresAPIRequester` at a mock HTTP server that returns a list with one CNPJ and one CPF. Assert that you get back a list of two `FornecedorToUpdate` objects with all fields populated correctly.

**Detectability:** Low. A field name mismatch would return `FornecedorToUpdate` objects with `None` values, which would then be passed to the adapter. The adapter might filter them out or propagate corrupt data before anyone notices.

---

### Priority 2 — `get_company()` happy path with null fields

**Why second:** Every fornecedor with a CNPJ triggers a call to `get_company()`. The `ReceitaAPIGetCompanyResponse` model has 25 optional fields — all `Optional[str]`. In practice, many real companies in the Receita API have missing data. If the deserialization fails for null values, every fornecedor with incomplete data fails to build.

**What to test:** Two scenarios back to back: one response with all 25 fields populated, and one response where every field is `null`. The second scenario is the critical one — verify the model deserializes without a `ValidationError` and every field is `None`.

**Why before the happy path with full data:** This is counter-intuitive. The full-data case is the normal path, but if Pydantic raises a `ValidationError` on nulls, the impact is broader — it breaks every company with any missing field, which in practice is most companies. The null-field scenario has higher real-world frequency.

---

### Priority 3 — `get_fornecedores_to_update()` error path (non-200)

**Why third:** The workflow catches and re-raises the exception from this method as `GetCNPJsToUpdateWorkflowError`. If the requester raises the wrong exception type (e.g., a raw `JSONDecodeError` from calling `response.json()` on a non-JSON body), the workflow's `except Exception as e` will still catch it — but the log entry will contain the wrong error class and wrong error message, making debugging in production very hard.

**What to test:** Make the mock server return a 500 with a non-JSON body (like `"Internal Server Error"` as plain text). Assert that `APIRequesterException` is raised — not `JSONDecodeError`. This test will likely reveal the bug described in section 3.1.

**Detectability:** Medium. The system would still stop and log an error, but the error message would be confusing. The real damage is to your ability to debug production issues.

---

### Priority 4 — `get_company()` 404 distinction

**Why fourth:** The code distinguishes between `RouteNotFoundError` (the route `/receita/api/v1/empresa-receita/get-by-cnpj/` doesn't exist) and `NotFoundError` (the CNPJ exists but the company isn't in the database). These two cases require different responses from the caller — one indicates a deployment problem (the API server is wrong), the other is a recoverable business condition.

If this distinction is wrong — e.g., the wrong exception is raised — the caller treats a deployment problem as a recoverable business error, keeps running, and silently produces zero results for every CNPJ.

**What to test:** Two 404 scenarios:
1. Response body: `{"detail": "Not Found"}` → assert `RouteNotFoundError`
2. Response body: `{"detail": "CNPJ não encontrado"}` → assert `NotFoundError`
3. Response body: `{}` (no `"detail"` key) → assert `NotFoundError`

**Detectability:** Low. Both exceptions are subclasses of `APIRequesterException`. The caller's code would behave differently depending on which one it catches, but if it only catches the base class, the difference is invisible until you look at the logs.

---

### Priority 5 — `get_municipio_by_name()` happy path

**Why fifth:** This runs for every fornecedor that has a city in the address — which is most of them, but not every one. The critical assumption here is the JSON key `"codigo_ibge"`. If the API returns a different key name, you get a raw `KeyError`. Test the happy path first to lock down the expected response shape.

---

### Priority 6 — `get_municipio_by_name()` error path

**Why last:** The 404 case raises `NotFoundError` unconditionally — there's no ambiguity like in `ReceitaAPIRequester`. The non-200 case raises `APIRequesterException`. These are straightforward. The main risk is the `response.json()` before the status check (same bug as `get_fornecedores_to_update()`), which your 500-with-non-JSON-body test will cover.

---

## 5. The Tests, Explained

Here is every test you need to write, with the reasoning behind each one. The "What you learn" column is the key: if you cannot answer what the test teaches you, the test should not exist.

### 5.1 `FornecedoresAPIRequester` — `get_fornecedores_to_update()`

#### Test 1 — Happy path with real-shaped data (Priority 1)

**Scenario:** Mock server returns HTTP 200 with a JSON array containing two objects — one with a raw CNPJ, one with a raw CPF. Both have all five fields: `loja`, `codigo`, `nome`, `nome_fantasia`, `cpf_cnpj`.

**Assert:**
- The method returns a `list` of two `FornecedorToUpdate` objects.
- `result[0].cpf_cnpj` equals the CNPJ string as returned by the server (the requester does not modify it).
- `result[1].cpf_cnpj` equals the CPF string as returned by the server.

**What you learn:** The URL is correct, the JSON field names match the `FornecedorToUpdate` model, and the deserialization does not silently drop or transform the `cpf_cnpj` field.

**Why this specific assertion:** The `cpf_cnpj` field is what the adapter uses to distinguish CPFs from CNPJs. If the requester parses it incorrectly (wrong field name, type coercion), the adapter receives wrong data. Testing this here, at the requester level, localizes the failure precisely.

---

#### Test 2 — Empty list (Priority 1)

**Scenario:** Mock server returns HTTP 200 with `[]`.

**Assert:** The method returns `[]` (not `None`, not raises an exception).

**What you learn:** The list comprehension `[FornecedorToUpdate(**f) for f in data]` handles an empty list correctly. This sounds obvious, but the return type annotation says `list[FornecedorToUpdate] | None` — you need to verify that the implementation never actually returns `None` from a 200 response.

---

#### Test 3 — Non-200 with a non-JSON body (Priority 3)

**Scenario:** Mock server returns HTTP 500 with `Content-Type: text/html` and body `"<html>Internal Server Error</html>"`.

**Assert:** `APIRequesterException` is raised.

**What you learn:** Whether the call to `response.json()` at the top of the method (before the status check) crashes with `JSONDecodeError` before reaching the `else` branch. If this test fails because `JSONDecodeError` is raised instead, you have found a real bug.

---

#### Test 4 — Non-200 with a JSON body (complementary to Test 3)

**Scenario:** Mock server returns HTTP 500 with `Content-Type: application/json` and body `{"error": "something went wrong"}`.

**Assert:** `APIRequesterException` is raised.

**What you learn:** This passes even if the `response.json()` bug exists (because the JSON parses fine), which confirms that the logic flow itself is correct when `response.json()` does not throw. If Test 3 fails but Test 4 passes, the bug is specifically the non-JSON body case.

---

### 5.2 `FornecedoresAPIRequester` — `get_municipio_by_name()`

#### Test 5 — Happy path (Priority 5)

**Scenario:** Mock server returns HTTP 200 for the path `/api/v1/municipios/name/MACEIO` with body `{"codigo_ibge": "2704302"}`.

**Assert:**
- The method returns a `Municipio`.
- `result.nome == "MACEIO"` (the name you passed in, not from the response).
- `result.codigo_ibge.value == "2704302"`.

**What you learn:** The URL path format is correct, the JSON key `"codigo_ibge"` is correct, and `CodigoMunicipioIBGE.create()` accepts a 7-digit string. The name comes from the input parameter (not the response) — if someone changes that, this test catches it.

**Why a real 7-digit IBGE code:** `CodigoMunicipioIBGE.create()` validates length. Using a realistic code (`"2704302"` is Maceió) makes the test meaningful and avoids accidentally hardcoding a fake code that the domain rejects.

---

#### Test 6 — 404 not found (Priority 6)

**Scenario:** Mock server returns HTTP 404 for any path.

**Assert:** `NotFoundError` is raised.

**What you learn:** The 404 branch is reached and raises the right exception type.

---

#### Test 7 — Non-200, non-404 with non-JSON body (Priority 6)

**Scenario:** Mock server returns HTTP 503 with `Content-Type: text/plain`.

**Assert:** `APIRequesterException` is raised (not `JSONDecodeError`).

**What you learn:** Same `response.json()` bug check as Test 3, but for this method.

---

### 5.3 `ReceitaAPIRequester` — `get_company()`

#### Test 8 — Happy path with all fields populated (Priority 2)

**Scenario:** Mock server returns HTTP 200 for the path `/receita/api/v1/empresa-receita/get-by-cnpj/28738609000181` with a full response body containing values for all 25 fields.

**Assert:**
- The method returns a `ReceitaAPIGetCompanyResponse`.
- Spot-check five or six specific fields: `CNPJ`, `NOME_EMPRESARIAL`, `END_LOGRADOURO`, `END_CEP`, `DDD1`, `EMAIL`.

**What you learn:** The URL path includes the CNPJ value correctly, the field names in the JSON match the model, and Pydantic deserializes the response without error.

**Why spot-check, not all 25 fields:** Asserting all 25 is brittle — if any field name changes in the future, you have to update 25 assertions. Spot-checking the most-used fields (the ones actually read by adapters downstream) catches real bugs without creating a maintenance burden.

---

#### Test 9 — Happy path with all fields as null (Priority 2)

**Scenario:** Mock server returns HTTP 200 with a JSON object where every field is explicitly `null`: `{"CNPJ": null, "NOME_EMPRESARIAL": null, ..., "HASH": null}`.

**Assert:**
- The method returns a `ReceitaAPIGetCompanyResponse`.
- Every field on the result is `None`.

**What you learn:** Pydantic's `model_validate()` handles `null` JSON values for every optional field without raising a `ValidationError`. This is the highest-priority test in the file because null fields are the most common real-world scenario.

---

#### Test 10 — 404 that should be `RouteNotFoundError` (Priority 4)

**Scenario:** Mock server returns HTTP 404 with body `{"detail": "Not Found"}`.

**Assert:** `RouteNotFoundError` is raised.

**What you learn:** The substring check `"Not Found" in response.json().get("detail")` matches this exact response body and raises the right exception.

---

#### Test 11 — 404 that should be `NotFoundError` (Priority 4)

**Scenario:** Mock server returns HTTP 404 with body `{"detail": "CNPJ não encontrado na base de dados"}`.

**Assert:** `NotFoundError` is raised.

**What you learn:** A 404 response with a detail message that does not contain `"Not Found"` raises `NotFoundError`, not `RouteNotFoundError`. This is the most important assertion about the distinction.

---

#### Test 12 — 404 with no `detail` key (Priority 4)

**Scenario:** Mock server returns HTTP 404 with body `{}`.

**Assert:** `NotFoundError` is raised.

**What you learn:** When `response.json().get("detail")` returns `None` (falsy), the condition short-circuits and falls through to `raise NotFoundError`. The code does not crash with an `AttributeError` from calling `.get()` on `None`.

---

#### Test 13 — Non-200, non-404 (Priority 3)

**Scenario:** Mock server returns HTTP 500 with body `{"detail": "Internal Server Error"}`.

**Assert:** `UnexpectedError` is raised.

**What you learn:** The `else` branch is reached and raises `UnexpectedError`. Because `ReceitaAPIRequester` calls `response.json()` inside each branch (not at the top), a JSON body is required here — but the test confirms the right exception type is raised.

---

## 6. Summary Table

| # | Method | Scenario | Exception or Result | Priority |
|---|---|---|---|---|
| 1 | `get_fornecedores_to_update` | 200 with CNPJ + CPF | `list[FornecedorToUpdate]` with both items | 1 |
| 2 | `get_fornecedores_to_update` | 200 with empty array | `[]` | 1 |
| 3 | `get_fornecedores_to_update` | 500 with non-JSON body | `APIRequesterException` | 3 |
| 4 | `get_fornecedores_to_update` | 500 with JSON body | `APIRequesterException` | 3 |
| 5 | `get_municipio_by_name` | 200 with valid IBGE code | `Municipio` with correct fields | 5 |
| 6 | `get_municipio_by_name` | 404 | `NotFoundError` | 6 |
| 7 | `get_municipio_by_name` | 503 with non-JSON body | `APIRequesterException` | 6 |
| 8 | `get_company` | 200 with all fields | `ReceitaAPIGetCompanyResponse` | 2 |
| 9 | `get_company` | 200 with all null fields | `ReceitaAPIGetCompanyResponse` with all `None` | 2 |
| 10 | `get_company` | 404 with `"detail": "Not Found"` | `RouteNotFoundError` | 4 |
| 11 | `get_company` | 404 with other detail | `NotFoundError` | 4 |
| 12 | `get_company` | 404 with no detail key | `NotFoundError` | 4 |
| 13 | `get_company` | 500 | `UnexpectedError` | 3 |

---

## 7. A Note on What These Tests Will Teach You About Your Code

As you implement these tests, you will encounter things that do not behave as expected. That is normal and valuable. When a test fails:

- **Read the actual exception type and message** before changing the test. The test might be correctly exposing a bug.
- **Ask yourself**: is the test wrong, or is the code wrong? If the test is testing the contract and the code does not fulfill it, fix the code.
- **Do not make the test pass by weakening the assertion.** `assert isinstance(result, Exception)` is not a test — it is a formality.

The goal is not to have green tests. The goal is to have tests that would turn red if the code broke. A test that always passes regardless of what the code does is worse than no test at all — it gives false confidence.

When you encounter a bug during this process (the `response.json()` before status check is the most likely candidate), note it, write a failing test that exposes it, then fix the code and confirm the test passes. That sequence — red, fix, green — is the rhythm of test-driven quality work.
