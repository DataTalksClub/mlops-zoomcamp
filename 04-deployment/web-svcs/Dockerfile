FROM python:3.10.11-slim

RUN pip install -U pip
RUN pip install pipenv 

WORKDIR /app

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "predict_lin.py", "lin_reg.bin", "./" ]

EXPOSE 5000

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:5000", "predict_lin:app" ]