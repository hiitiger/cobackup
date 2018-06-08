import functools
import time

def blocking_throttle(max_per_seconds):
    assert max_per_seconds > 0
    wait_interval = 1.0 / float(max_per_seconds)
    def decorate(func):
        last_time = [0.0]
        @functools.wraps(func)
        def block_throttle_control(*args, **kwargs):
            elapsed_time = time.time() - last_time[0]
            wait_time = wait_interval - elapsed_time
            if wait_time > 0:
                time.sleep(wait_time)
            last_time[0] = time.time()
            return func(*args, **kwargs)
        return block_throttle_control
    return decorate

# @blocking_throttle(2/1)
# def call(a):
#     print(a)

# for i in range(0, 4):
#     call(i)