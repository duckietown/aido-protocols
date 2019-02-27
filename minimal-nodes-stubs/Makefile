
test-all_connected:
	cat  dummy_image_source/test_data/in1.json | \
	./dummy_image_source/dummy_image_source.py run --name source1 | \
	./dummy_image_filter/dummy_image_filter.py run --name node1   | \
	./dummy_image_filter/dummy_image_filter.py run --name node2
