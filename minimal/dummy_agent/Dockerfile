FROM python:3.7

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["aido_node_wrap", "--implementation", "random_agent.RandomAgent", "--protocol",  "aido_nodes.protocol_agent_jpg_pwm"]
