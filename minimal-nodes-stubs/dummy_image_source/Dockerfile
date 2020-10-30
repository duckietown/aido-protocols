ARG AIDO_REGISTRY
FROM ${AIDO_REGISTRY}/duckietown/aido-base-python3:daffy-amd64

ARG PIP_INDEX_URL
ENV PIP_INDEX_URL=${PIP_INDEX_URL}


COPY requirements.* ./
RUN cat requirements.* > .requirements.txt
RUN  pip3 install --use-feature=2020-resolver -r .requirements.txt


COPY . .


ENTRYPOINT ["python", "dummy_image_source.py"]

