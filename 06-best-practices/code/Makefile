ENV=dev

.PHONY: init plan validate apply destroy build_packages zip_main_py zip_main_async_py unittests tests

all:  init  plan

init:
	cd infrastructure && terraform init  -reconfigure

plan:
	cd infrastructure && terraform plan

validate:
	cd infrastructure && terraform validate

apply:
	cd infrastructure && terraform apply -auto-approve

destroy:
	cd infrastructure && terraform destroy -auto-approve

build_packages:
	mkdir -p aws_lambda/package && pip3 install -r aws_lambda/requirements.txt --target  aws_lambda/package --upgrade

unittests:
	cd aws_lambda && python3 -m unittest discover

tests:	unittests	validate