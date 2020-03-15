ARG AIDO_REGISTRY
FROM ${AIDO_REGISTRY}/duckietown/aido-base-python3:daffy-aido4

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm -rf /root/.cache

COPY . .


ENTRYPOINT ["python", "dummy_image_source.py"]

