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
