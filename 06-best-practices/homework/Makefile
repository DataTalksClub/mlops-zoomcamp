quality_checks:
	find . -type f -name "*.py" | xargs pylint
	black .
	isort .

unit_tests: quality_checks
	pipenv run pytest tests/ 

integration_tests: unit_tests
	bash ./integration-tests/run.sh
