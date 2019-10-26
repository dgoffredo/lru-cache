
import functools
import time

@functools.lru_cache(maxsize=3)
def slow_square(x):
    print('shhh...')
    time.sleep(1)
    return x**2


print(slow_square(3))
print(slow_square(3))
print(slow_square(3))

print(slow_square(2))
print(slow_square(2))
print(slow_square(2))

print(slow_square(1))
print(slow_square(1))
print(slow_square(1))

print(slow_square(5))
print(slow_square(5))
print(slow_square(5))

# This will take a second, because `3` was evicted from the cache just above.
print(slow_square(3))