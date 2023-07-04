FROM svizor/zoomcamp-model:mlops-3.10.0-slim

RUN pip install -U pip & pip install pipenv

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "batch.py", "batch.py" ]

ENTRYPOINT [ "python", "batch.py" ]