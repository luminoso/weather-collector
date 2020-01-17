FROM python:3-alpine

WORKDIR .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sources ./sources
COPY outputs ./outputs
COPY utils ./utils/
COPY config.yaml .
COPY *.py ./

ENTRYPOINT [ "python", "./weather-collector.py" ]
