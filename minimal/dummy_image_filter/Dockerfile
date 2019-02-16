FROM python:3.7

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["aido_node_wrap",
            "--implementation", "dummy_image_filter.DummyFilter",
            "--protocol",  "aido_nodes.protocol_image_filter"]
