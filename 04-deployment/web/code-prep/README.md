

Preparing the environment:

```bash
pip install -U pipenv
pipenv install
```

Running the service:

```bash
pipenv run python main.py
```

Testing the service:

```bash
python test.py
```

Building the Docker image:

```bash
docker build -t duration:v1 .
```

Running the Docker image:

```bash
docker run -it --rm \
    -p 9696:9696 \
    duration:v1
```

Testing the service:

```bash
python test.py
```