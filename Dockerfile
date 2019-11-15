FROM python:3-alpine

WORKDIR .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ipma ./ipma/
COPY ipma_unofficial ./ipma_unofficial/
COPY utils ./utils/
COPY config.yaml .
COPY *.py ./

ENTRYPOINT [ "python", "./weather-collector.py" ]
