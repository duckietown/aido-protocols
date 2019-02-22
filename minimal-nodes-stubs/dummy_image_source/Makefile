tag=dummy_image_source

build:
	docker build -t $(tag) .

build-no-cache:
	docker build -t $(tag)  --no-cache .

test-data1-direct:
	./dummy_image_source.py run < test_data/in1.json > test_data/out1.json

test-data1-docker:
	docker run -i $(tag) run < test_data/in1.json > test_data/out1.json


#
#protocols=/data/work/vmware-michela-shared/DT/dt-env/dt-env-developer/src/aido-protocols
#
#other=-v $(protocols):/src/aido-protocols/
#other=
