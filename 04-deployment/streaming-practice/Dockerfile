FROM public.ecr.aws/lambda/python:3.9

RUN pip install -U pip 
RUN pip install -U pipenv 

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY [ "lambda_function.py", "./" ]

CMD [ "lambda_function.lambda_handler" ]
