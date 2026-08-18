# How to Properly Mock the HTTP Server in Integration Tests

## The Anatomy of One Test First

Before practices, internalize the pattern every test in this file will follow:

```python
from pytest_httpserver import HTTPServer
from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester

@pytest.mark.integration_tests
def test_should_return_list_of_fornecedores_to_update_when_api_returns_200(
    httpserver: HTTPServer,
):
    # 1. Define what the server expects and returns
    httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json([
        {"loja": "01", "codigo": "100", "nome": "Empresa X", "nome_fantasia": "X", "cpf_cnpj": "62173620000180"},
    ])

    # 2. Point the real requester at the mock server
    requester = FornecedoresAPIRequester(base_url=httpserver.url_for(""))

    # 3. Call the real method
    result = requester.get_fornecedores_to_update()

    # 4. Assert on the result
    assert len(result) == 1
    assert result[0].cpf_cnpj == "62173620000180"
```

Three things are real here: the `FornecedoresAPIRequester`, the `requests.get()` call inside it, and the JSON parsing. The only thing controlled is what the server responds with. That is what makes it an integration test.

---

## Practice 1: Never hardcode the port — always use `httpserver.url_for("")`

`pytest-httpserver` picks a free port automatically. If you hardcode `"http://localhost:8080"`, the test will fail whenever that port is in use on your machine or in CI.

```python
# Wrong
requester = FornecedoresAPIRequester(base_url="http://localhost:8080")

# Right
requester = FornecedoresAPIRequester(base_url=httpserver.url_for(""))
```

`httpserver.url_for("")` returns `"http://localhost:{dynamic_port}"`. Pass it as `base_url` — that is exactly what your constructor receives in production (`settings.FORNECEDORES_API_BASE_URL`), so the test faithfully mirrors the real wiring.

---

## Practice 2: Match the path exactly — and let that be one of your assertions

`expect_request` takes the path as a string. Be precise:

```python
# Right — tests that the URL path is exactly what the API expects
httpserver.expect_request("/api/v1/fornecedores-to-update")

# Wrong — too loose, doesn't verify the path at all
httpserver.expect_request("/")
```

The reason this matters: if someone changes the URL template in the requester from `/api/v1/fornecedores-to-update` to `/api/v2/fornecedores-to-update`, the mock server will not match the request. At test teardown, `pytest-httpserver` raises `AssertionError: expected request was not made`. The path check is a free assertion you get without writing a single `assert` statement.

---

## Practice 3: Use `respond_with_json` for JSON, `respond_with_data` for everything else

`respond_with_json` does two things: serializes the dict to JSON and sets `Content-Type: application/json`. Use it for all 200 responses and for non-200 responses where the body happens to be JSON.

```python
# 200 with a JSON array
httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json([...])

# 500 with a JSON body (still a valid JSON response, just an error status)
httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json(
    {"error": "internal server error"},
    status=500,
)
```

For the non-JSON body test — the bug-revealing one — you must use `respond_with_data` and explicitly set the content type. If you forget the content type, `requests` might still try to parse it as JSON:

```python
# The non-JSON body test
httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_data(
    "<html><body>Internal Server Error</body></html>",
    content_type="text/html",
    status=500,
)
```

The distinction is important: `respond_with_json(data, status=500)` still has a parseable JSON body — `response.json()` would succeed — so `APIRequesterException` would be raised correctly. That is test [C] from the grid. `respond_with_data(..., content_type="text/html", status=500)` has a non-parseable body — `response.json()` crashes — that is test [D], the one that reveals the bug.

---

## Practice 4: Keep test data minimal, but use the real field names

Your test data only needs to contain what your assertion checks. But the field names must match `FornecedorToUpdate` exactly, because that is what you are testing:

```python
# Good — minimal, but correct field names
httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json([
    {"loja": "01", "codigo": "100", "nome": "Empresa X", "nome_fantasia": "X", "cpf_cnpj": "62173620000180"},
])

# Bad — missing required fields (would cause ValidationError in your code, which is not what you want to test here)
httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json([
    {"cpf_cnpj": "62173620000180"},
])

# Bad — invented field names that don't match the model (wrong test data defeats the purpose)
httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json([
    {"cpfCnpj": "62173620000180"},
])
```

The last example is the tricky one. You might think "I should test what happens if the API uses camelCase." But that is not the test for this method — the test for `get_fornecedores_to_update` is "does the method correctly parse the expected response shape." If the real API ever changes its field names, that will break the test naturally because the real data will no longer match the model.

---

## Practice 5: One expectation per test, defined at the top

Define the mock at the top of the test, before calling any production code. This makes the test readable as a three-part story: setup, act, assert.

```python
def test_should_return_empty_list_when_api_returns_empty_array(httpserver: HTTPServer):
    # Setup — what the server will return
    httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json([])

    # Act — call the real code
    requester = FornecedoresAPIRequester(base_url=httpserver.url_for(""))
    result = requester.get_fornecedores_to_update()

    # Assert — verify the result
    assert result == []
```

Never define the mock inside an `if` or after the production code call. The mock is part of your test setup — it describes the world the code runs in.

---

## Practice 6: Know what `pytest-httpserver` verifies automatically

When you call `expect_request`, you are registering a contract: "I expect this request to be made." At the end of the test, if the request was never made, `pytest-httpserver` fails the test with `AssertionError`.

This means **you never need to assert that `requests.get` was called**. The teardown does it for you. What you assert is the return value or exception:

```python
def test_should_raise_api_requester_exception_when_api_returns_non_200_with_json_body(
    httpserver: HTTPServer,
):
    httpserver.expect_request("/api/v1/fornecedores-to-update").respond_with_json(
        {"error": "something went wrong"},
        status=500,
    )

    requester = FornecedoresAPIRequester(base_url=httpserver.url_for(""))

    with pytest.raises(APIRequesterException):
        requester.get_fornecedores_to_update()

    # No need to assert "requests.get was called" — httpserver does that at teardown
```

---

## The Anti-Pattern to Avoid

The temptation when writing HTTP client tests is to do this:

```python
from unittest.mock import patch

def test_something():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [...]
        result = requester.get_fornecedores_to_update()
```

This is not an integration test. It patches `requests.get` at the Python level — no real HTTP call happens, no real TCP connection, no real JSON serialization. It is a unit test wearing integration test clothing. The bug on Line 3 (`response.json()` before the status check) would not be caught by this approach, because you are directly controlling `mock_get.return_value.json.return_value` — you bypass the execution order entirely.

`pytest-httpserver` makes a real HTTP call through the full `requests` stack. The execution order in your code is exactly what runs in production. That is the point.
