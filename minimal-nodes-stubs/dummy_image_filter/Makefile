tag=dummy_image_filter

build:
	docker build -t $(tag) .

build-no-cache:
	docker build -t $(tag)  --no-cache .

test-data1-direct:
	./dummy_image_filter.py run < test_data/in1.json > test_data/out1.json

test-data1-docker:
	docker run -i $(tag) run < test_data/in1.json > test_data/out1.json


test-data1-direct-more:
	cat  test_data/in1.json | \
		./dummy_image_filter.py run --name node1  | \
		./dummy_image_filter.py run --name node2  \
		> test_data/out1.json
