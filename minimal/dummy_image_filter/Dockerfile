FROM python:3.7

COPY . .
RUN pip install -r requirements.txt

CMD aido_node_wrap --implementation dummy_image_filter.DummyFilter --protocol aido_nodes.image_filter
