LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
export LOCAL_IMAGE_NAME:=stream-model-duration:${LOCAL_TAG}
quality_checks:
	find . -type f -name "*.py" | xargs pylint
	black .
	isort .
	pipenv run pytest tests/ 

build: quality_checks
	docker build -t ${LOCAL_IMAGE_NAME} .

integration_tests: build
	bash ./integration-test/run.sh

publish: integration_tests
	echo Publishing the image to AWS
	bash pushEcr.sh

setup:
	pipenv install --dev 
	pre-commit install
	