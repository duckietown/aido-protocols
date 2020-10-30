
AIDO_REGISTRY ?= docker.io
PIP_INDEX_URL ?= https://pypi.org/simple

repo=aidonode-dummy_image_source
# repo=$(shell basename -s .git `git config --get remote.origin.url`)
branch=$(shell git rev-parse --abbrev-ref HEAD)
tag=$(AIDO_REGISTRY)/duckietown/$(repo):$(branch)


build_options=\
 	--build-arg AIDO_REGISTRY=$(AIDO_REGISTRY)\
 	--build-arg PIP_INDEX_URL=$(PIP_INDEX_URL)

update-reqs:
	pur --index-url $(PIP_INDEX_URL) -r requirements.txt -f -m '*' -o requirements.resolved
	#dt-update-reqs requirements.resolved

build: update-reqs
	docker build --pull -t $(tag) $(build_options) .

build-no-cache: update-reqs
	docker build --pull -t $(tag) $(build_options) --no-cache .

push: build
	dts build_utils push $(tag)


test-data1-direct:
	./dummy_image_source.py < test_data/in1.json > test_data/out1.json

test-data1-docker:
	docker run -i $(tag) < test_data/in1.json > test_data/out1.json

test-describe:
	./dummy_image_source.py < test_data/describe.json

#
#protocols=/data/work/vmware-michela-shared/DT/dt-env/dt-env-developer/src/aido-protocols
#
#other=-v $(protocols):/src/aido-protocols/
#other=
