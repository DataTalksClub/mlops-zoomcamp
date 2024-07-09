FROM public.ecr.aws/lambda/python:3.10

RUN pip install -U pip
RUN pip install pipenv
#RUN pip install awscli

#RUN --mount=type=secret,id=aws,target=/root/.aws/credentials \
#    aws s3 cp s3://... /app/...
# USER 0

# RUN mkdir /root/.aws

# #COPY /c/Users/ArunGanesan/.aws  /root/.aws
# COPY [ "credentials", "config", "/root/.aws" ]

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "lambda_function.py", "./" ]

CMD [ "lambda_function.lambda_handler" ]
