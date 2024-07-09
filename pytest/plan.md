## Plan

- [x] Testing the code: unit tests with pytest
- [x] Integration tests with docker-compose
- [x] Testing cloud services with LocalStack
- [x] Code quality: linting and formatting
- [x] Git pre-commit hooks
- [x] Makefiles and make
- [ ] Staging and production environments
- [ ] Infrastructure as Code
- [ ] CI/CD and GitHub Actions


PEP 8 – Style Guide for Python Code
https://peps.python.org/pep-0008/

What is Pylint?
Pylint analyses your code without actually running it. It checks for errors, enforces a coding standard, looks for code smells, and can make suggestions about how the code could be refactored.

pipenv install --dev pylint

#run pylint on all the files and folders under the current working directory which has a .py extension
pylint --recursive=y .

select Linter in VSCode shift+ctrl+p 

https://www.codeac.io/documentation/pylint-configuration.html

use .pylintrc file to configure which pylint warnings can be ignored

you can use pyproject.toml to configure linting for your project instead of pylint

## library for formatting
pipenv install --dev black 

## libary for sorting import of libraries
pipenv install --dev isort


## black will replace single quotes with double quotes
## investigat black on the current folder. Don't write the files back, just output a diff to indicate what changes Black would've made. 
black --diff .

black --diff . | less

# apply the changes of formatting using black
black .

#get the modified git repository fies
git status

#add the modified git repository files to master from the current working directory
git add .

#commit the changes to the master branch
git commit -m "comments on commit"

#push the changes to the master branch
#use "git push" to publish your local commits
git push 

# analyze the changes proposed by isort to the current working directory
isort --diff . | less

# compare file from local branch to master branch
git diff <filename>

Order of application
isort .
black .
pylint --recursive=y .
pytest tests/
$pwd/integration-test/run.sh


# do a bunch of checks and balances on the pythong package before committing the same to git repository
#install pre-commit checks
pipenv install --dev pre-commit


