FROM python:3.7

ENV PROJECT_DIR /app

WORKDIR ${PROJECT_DIR}
COPY . ${PROJECT_DIR}

RUN apt update
RUN apt install -y zip
RUN pip install -r requirements.txt

