FROM python:3.7
WORKDIR /project

RUN pip install -U pip
COPY requirements.txt requirements-base.txt
RUN pip install -r requirements-base.txt

RUN apt-get update && apt-get install -y ffmpeg mencoder && apt-get clean
