FROM python:3.7
WORKDIR /project

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN apt-get install python3

ENTRYPOINT ["python", "dummy_image_source.py"]
