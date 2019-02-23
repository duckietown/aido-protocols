tag=dummy_agent

build:
	docker build -t $(tag) .

build-no-cache:
	docker build -t $(tag)  --no-cache .

test-data1-direct:
	./random_agent.py run < test_data/in1.json > test_data/out1.json

test-data1-docker:
	docker run -i $(tag) run < test_data/in1.json > test_data/out1.json
