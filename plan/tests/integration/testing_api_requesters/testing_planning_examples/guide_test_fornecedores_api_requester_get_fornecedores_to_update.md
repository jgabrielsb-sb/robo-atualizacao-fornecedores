# How to Think About Integration Testing: `get_fornecedores_to_update`

## The Core Shift: Read Code as a Suspicious Reader

When you write unit tests, you read the code as its author — you know the intent, so you test the intent. Integration tests require a different posture: **read the code as someone who does not trust that the world will cooperate.**

Every line of this method makes an assumption about the external world. Your job is to find each assumption, ask "what if this assumption is wrong?", and write a test for each answer that matters.

Let's do this line by line.

---

## Reading the Method Line by Line

```python
def get_fornecedores_to_update(self) -> list[FornecedorToUpdate] | None:
    url = f"{self._base_url}/api/v1/fornecedores-to-update"  # Line 1
    response = requests.get(url)                              # Line 2
    data = response.json()                                    # Line 3 ← suspicious
    status_code = response.status_code                        # Line 4

    if status_code == HTTPStatus.OK:                          # Line 5
        return [FornecedorToUpdate(**fornecedor) for fornecedor in data]  # Line 6
    else:
        raise APIRequesterException(...)                      # Line 7
```

**Line 1:** Builds a URL from `base_url`. No assumptions about the world yet — this is pure string construction.

**Line 2:** Makes a real HTTP call. In the integration test, this will hit your mock server.

**Line 3:** `data = response.json()`. This is the most important line to stare at. It is called **before** the status code is checked. It assumes the response body is always parseable as JSON — regardless of what the server returned. If the server returns a 500 with an HTML error page (which is common), `response.json()` will raise a `JSONDecodeError` right here, and the code never reaches Line 7. Your caller will receive a `JSONDecodeError`, not an `APIRequesterException`.

**Line 5–6:** If status is 200, it tries to deserialize `data` as a list of dicts, each matching `FornecedorToUpdate`. This assumes:
- `data` is a list (not `null`, not a single object)
- Each element has exactly these keys: `loja`, `codigo`, `nome`, `nome_fantasia`, `cpf_cnpj` — because they are all `str` and required in the Pydantic model. A missing key or a `null` value raises `ValidationError`.

**Line 7:** Raises `APIRequesterException` — but only if Line 3 didn't crash first.

---

## From Suspicious Reading to Input Space

After reading suspiciously, you have a map of every dimension that can vary in the input — in this case, the HTTP response. An HTTP response has exactly two independent dimensions that affect behavior here:

- **Status code**: either 200 or something else (non-200)
- **Body**: either parseable as JSON, or not

Draw the grid:

```
                  | Body: valid JSON  | Body: non-JSON
------------------+------------------+----------------
Status: 200       |      [A]         |      [B]
Status: non-200   |      [C]         |      [D]
```

Now ask: **what should the method do in each cell?**

- **[A] 200 + valid JSON**: return the list. But "valid JSON" has a sub-case — what if the array is empty `[]`? That is a separate behavior worth verifying. Split [A] into [A1] non-empty and [A2] empty.
- **[B] 200 + non-JSON**: the server is broken. `response.json()` will throw `JSONDecodeError`. There is no good behavior here — this is already an unexpected situation. You do not need a test for this because both you and your caller agree this is an unhandled edge case.
- **[C] non-200 + valid JSON**: `response.json()` succeeds, status check hits the `else` branch, `APIRequesterException` is raised. This is what the code intends.
- **[D] non-200 + non-JSON**: `response.json()` at Line 3 throws `JSONDecodeError` before the `else` branch is ever reached. The contract says `APIRequesterException`, but the actual behavior is `JSONDecodeError`. **This is a bug.**

You now have exactly **four scenarios** worth testing: [A1], [A2], [C], and [D]. That is not a coincidence — it is the result of exhaustively partitioning the input space.

---

## The Four Tests

```python
def test_should_return_list_of_fornecedores_to_update_when_api_returns_200():
    ...

def test_should_return_empty_list_when_api_returns_empty_array():
    ...

def test_should_raise_api_requester_exception_when_api_returns_non_200_with_json_body():
    ...

def test_should_raise_api_requester_exception_when_api_returns_non_200_with_non_json_body():
    ...
```

Each test maps to exactly one cell. No overlap, no gap.

---

## Why Exactly These Four and Not More

**Why `test_should_return_list_of_fornecedores_to_update_when_api_returns_200`?**

This is the test that verifies the whole chain works: the URL path is correct (the mock server will reject it if it is not), the JSON field names match the `FornecedorToUpdate` model exactly, and the deserialization produces the right Python objects. Without this test, you have zero confidence the happy path works at all.

**Why `test_should_return_empty_list_when_api_returns_empty_array`?**

`[]` is a boundary condition. The list comprehension `[FornecedorToUpdate(**f) for f in data]` returns `[]` when `data` is empty — but the return type annotation says `list[FornecedorToUpdate] | None`. That `| None` suggests the author considered returning `None`. You need to verify the method actually returns `[]` and not `None`, because the caller (`GetCNPJsToUpdateViaFornecedoresAPIRequester`) does `for fornecedor in result` — iterating over `None` crashes; iterating over `[]` does not.

**Why `test_should_raise_api_requester_exception_when_api_returns_non_200_with_json_body`?**

This verifies that the error path works when conditions are favorable — the JSON parses fine, the status check hits `else`, the right exception is raised. If this test fails, the problem is the `if/else` logic, not the JSON parsing.

**Why `test_should_raise_api_requester_exception_when_api_returns_non_200_with_non_json_body`?**

This is the bug-revealing test. It represents what many real servers actually return on a 500 — an HTML error page, a plain text message, a gateway timeout response with no body. The test will likely **fail** because `response.json()` crashes before `APIRequesterException` is raised. That failing test is the test working correctly — it found a real bug. When you see it fail, your next step is to fix the code so the method always raises `APIRequesterException` on non-200 responses, regardless of the body format.

---

## The Principle Behind This Thinking

You are not writing tests from a list of "things to check." You are doing three steps in sequence:

1. **Read the code as a suspicious reader** — find every assumption a line makes about the external world.
2. **Map the input space** — enumerate the states the external world can be in.
3. **Derive one test per distinct behavior** — each cell in your grid that produces a different observable outcome gets a test.

If you follow these steps, you will never write a test that duplicates another, and you will never miss a test that matters.
