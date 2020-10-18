AIDO_REGISTRY ?= docker.io
PIP_INDEX_URL ?= https://pypi.org/simple

build:
	make -C dummy_image_source build
	make -C dummy_image_filter build
	make -C dummy_simulator    build
	make -C random_agent       build

build-no-cache:
	make -C dummy_image_source build-no-cache
	make -C dummy_image_filter build-no-cache
	make -C dummy_simulator    build-no-cache
	make -C random_agent       build-no-cache


push: build
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
	AIDONODE_ENCODING=cbor AIDONODE_NAME=node2   AIDONODE_META_OUT=meta.json ./dummy_image_filter/dummy_image_filter.py  > res2.cbor


build_options=\
 	--build-arg AIDO_REGISTRY=$(AIDO_REGISTRY)\
 	--build-arg PIP_INDEX_URL=$(PIP_INDEX_URL)

test-docker-build: build
	docker-compose build $(build_options)

test-docker-up: test-docker-build
	docker-compose up #--build

