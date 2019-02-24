from comptests import comptest, run_module_tests


@comptest
def dummy1():
    pass


@comptest
def dummy2():
    pass


@comptest
def dummy3():
    pass


@comptest
def dummy4():
    pass


@comptest
def dummy5():
    pass


if __name__ == '__main__':
    run_module_tests()
