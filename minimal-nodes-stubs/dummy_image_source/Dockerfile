FROM duckietown/aido3-base-python3:daffy

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm -rf /root/.cache

COPY . .


ENTRYPOINT ["python", "dummy_image_source.py"]

