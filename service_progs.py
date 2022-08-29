import time


def time_of_function(function):
    def wrapped(*args):
        start_time = time.perf_counter_ns()
        res = function(*args)
        print(function.__name__, " ", time.perf_counter_ns() - start_time)
        return res

    return wrapped
