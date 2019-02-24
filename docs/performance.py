# import json
import timeit

import cbor2
import cbor

import numpy as np
import pybase64 as base64
import ujson as json


def bytes_to_json(jpg_bytes: bytes) -> str:
    data = {
        'jpg_bytes': base64.b64encode(jpg_bytes).decode('ascii')
    }
    return json.dumps(data).encode('utf-8')


def bytes_to_cbor(jpg_bytes: bytes) -> bytes:
    data = {
        'jpg_bytes': jpg_bytes,
    }
    return cbor.dumps(data)




def bytes_to_cbor_b64(jpg_bytes: bytes) -> bytes:
    data = {
        'jpg_bytes': base64.b64encode(jpg_bytes).decode('ascii')
    }
    return cbor.dumps(data)


def bytes_to_cbor2(jpg_bytes: bytes) -> bytes:
    data = {
        'jpg_bytes': jpg_bytes,
    }
    return cbor2.dumps(data)


def bytes_to_cbor2_b64(jpg_bytes: bytes) -> bytes:
    data = {
        'jpg_bytes': base64.b64encode(jpg_bytes).decode('ascii')
    }
    return cbor2.dumps(data)



def get_jpg_image(shape) -> bytes:
    H, W = shape
    values = (128 + np.random.randn(H, W, 3) * 60).astype('uint8')
    jpg_data = bgr2jpg(values)
    return jpg_data


def bgr2jpg(image_cv) -> bytes:
    import cv2
    # noinspection PyUnresolvedReferences
    compress = cv2.imencode('.jpg', image_cv)[1]
    jpg_data = np.array(compress).tostring()
    return jpg_data


N = 3
shape = (480 * N, 640 * N)
test_image: bytes = get_jpg_image(shape)


# f = open('stream.bin', 'wb')
def test1():
    """ JSON with base64"""
    res = bytes_to_json(test_image)

def test2():
    """ CBOR with base64"""
    res = bytes_to_cbor_b64(test_image)

def test3():
    """ CBOR with built-in bytes"""
    res = bytes_to_cbor(test_image)

def test4():
    """ CBOR2 with base64"""
    res = bytes_to_cbor2_b64(test_image)

def test5():
    """ CBOR2 with built-in bytes"""
    res = bytes_to_cbor2(test_image)


number = 800


for f in [test3, test2,  test4, test5, test1,]:
    f() # warmup

    duration = timeit.timeit(f, number=number)


    latency_ms = duration / number * 1000
    size = '%d KB' % (len(test_image) / 1024)
    print(f'{f.__doc__}: shape {shape} ({size}) latency = {latency_ms} ms')
#
# duration = timeit.timeit(test2, number=number)
#
# latency_ms = duration / number * 1000
# size = '%d KB' % (len(test_image) / 1024)
# print(f'CBOR encoding: shape {shape} ({size}) latency = {latency_ms} ms')
#
# with open('test_vector.jpg', 'wb') as f:
#     f.write(test_image)

