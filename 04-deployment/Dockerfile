FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

# do stuff here
RUN pip install -U pip
RUN pip install pipenv
#RUN pip install numpy==1.26.4 pandas==2.2.2 scikit-learn==1.5.0 pyarrow==15.0.2


WORKDIR /app
RUN mkdir -p /app/output/yellow
#COPY [ "model2.bin", "model.bin" ] # buildkit. Not copying thr model becaude the image at the first line already has the vectorizer and model picke files

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "starter-hw.py",  "./" ]

ENTRYPOINT [ "python","starter-hw.py" ]