.PHONY: clean run-unit-tests run-integration-tests run-fast-tests run-real-cases run-all-tests run

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.py[co]" -delete
	find . -type f -name "*~" -delete

run-unit-tests:
	uv run pytest -vv --html=report.html -m "unit"

run-integration-tests:
	uv run pytest -vv --html=report.html -m "integration_tests"

run-fast-tests:
	uv run pytest --html=report.html -m "not real_case_tests"

run-real-cases:
	uv run pytest --html=report.html -m "real_case_tests"

run-all-tests:
	uv run pytest --html=report.html

run:
	uv run python src/main.py
