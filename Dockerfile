FROM python:3.7

RUN apt update && apt install -y zip && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY src /app