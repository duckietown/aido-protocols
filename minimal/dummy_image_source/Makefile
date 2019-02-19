tag=dummy_image_source

build:
	docker build -t $(tag) .
build-no-cache:
	docker build -t $(tag)  --no-cache .

protocols=/data/work/vmware-michela-shared/DT/dt-env/dt-env-developer/src/aido-protocols

other=-v $(protocols):/src/aido-protocols/

test:
	docker run -i $(other) $(tag) describe-protocol
	docker run -i $(other) $(tag) run


test-data1-direct:
	./dummy_image_source.py run < test_data/in.json > test_data/out1.json

test-data1-docker:
	docker run -i $(other) $(tag) run < test_data/in.json > test_data/out2.json
