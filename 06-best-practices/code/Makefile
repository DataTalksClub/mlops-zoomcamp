LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"

test:
	pytest tests/

quality_checks:
	isort .
	black .
	pylint --recursive=y .


build: quality_checks test
	docker build -t ${LOCAL_IMAGE_NAME} ..

integration_test: build
	bash integraton-test/run.sh


publish: build
