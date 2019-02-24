from comptests import comptest, run_module_tests


@comptest
def dummy1():
    pass


if __name__ == '__main__':
    run_module_tests()
