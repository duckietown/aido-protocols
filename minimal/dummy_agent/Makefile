tag=dummy_agent

build:
	docker build -t $(tag) .
build-no-cache:
	docker build -t $(tag)  --no-cache .

test:
	docker run -i $(tag) describe-protocol
	docker run -i $(tag) run < data.json
