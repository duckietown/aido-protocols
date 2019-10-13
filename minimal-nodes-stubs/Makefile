
build:
	make -C aido3-base-python3 build
	make -C dummy_image_source build
	make -C dummy_image_filter build
	make -C dummy_simulator    build
	make -C random_agent       build

build-no-cache:
	make -C aido3-base-python3 build-no-cache
	make -C dummy_image_source build-no-cache
	make -C dummy_image_filter build-no-cache
	make -C dummy_simulator    build-no-cache
	make -C random_agent       build-no-cache


push:
	make -C aido3-base-python3 push
	make -C dummy_image_source push
	make -C dummy_image_filter push
	make -C dummy_simulator    push
	make -C random_agent       push

test-all_connected:
	cat  dummy_image_source/test_data/in1.json | json2cbor | \
	AIDONODE_NAME=source1 AIDONODE_META_OUT=meta.json ./dummy_image_source/dummy_image_source.py  | \
	AIDONODE_NAME=node1   AIDONODE_META_OUT=meta.json ./dummy_image_filter/dummy_image_filter.py  | \
	AIDONODE_NAME=node2   AIDONODE_META_OUT=meta.json ./dummy_image_filter/dummy_image_filter.py   > res1.cbor

test-all_connected-cbor:
	cat  dummy_image_source/test_data/in1.json | json2cbor | \
	AIDONODE_ENCODING=cbor AIDONODE_NAME=source1 AIDONODE_META_OUT=meta.json ./dummy_image_source/dummy_image_source.py  | \
	AIDONODE_ENCODING=cbor AIDONODE_NAME=node1   AIDONODE_META_OUT=meta.json ./dummy_image_filter/dummy_image_filter.py  | \
	AIDONODE_ENCODING=cbor AIDONODE_NAME=node2   AIDONODE_META_OUT=meta.json ./dummy_image_filter/dummy_image_filter
	.py  > res2.cbor

test-docker-build: build
	docker-compose build

test-docker-up: build
	docker-compose up --build

