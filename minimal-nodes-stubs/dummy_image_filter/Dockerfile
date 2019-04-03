FROM duckietown/aido2-base-python3:v4

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm -rf /root/.cache

COPY . .

ENTRYPOINT ["python3", "dummy_image_filter.py"]
