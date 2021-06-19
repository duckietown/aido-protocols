ARG AIDO_REGISTRY
FROM ${AIDO_REGISTRY}/duckietown/aido-base-python3:daffy-amd64

ARG PIP_INDEX_URL="https://pypi.org/simple"
ENV PIP_INDEX_URL=${PIP_INDEX_URL}


COPY requirements.* ./
RUN cat requirements.* > .requirements.txt
RUN  pip3 install  -r .requirements.txt


COPY . .


ENTRYPOINT ["python", "dummy_image_source.py"]

