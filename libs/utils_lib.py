import time

def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kw):
        tstart = time.time()
        output = my_func(*args, **kw)
        tend = time.time()
        diff = (tend - tstart) * 1000
        return output, diff
    return timed


class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()
        return self.start_time

    def stop(self):
        self.end_time = time.time()

    def reset(self):
        self.start_time = None
        self.end_time = None

    def time(self, unit="ms"):
        diff = (self.end_time - self.start_time)
        if unit == "ms":
            return diff * 1000