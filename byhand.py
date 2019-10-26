
# Use a doubly-linked list to keep track of when a cached value was most
# recently queried.  Elements not in the cache just get appended to the
# linked list.  When an element in the cache is accessed, its corresponding
# linked list node is removed from and then appended to the linked list.  When
# the cache is full, the front of the linked list is removed and the
# corresponding item in the cache is evicted.

class LinkedList:
    class Node:
        def __init__(self, value=None, before_me=None, after_me=None):
            self.value = value
            self.before_me = before_me
            self.after_me = after_me

    def __init__(self):
        self.head = LinkedList.Node()
        self.tail = LinkedList.Node(before_me=self.head)
        self.head.after_me = self.tail

    def remove_node(self, node):
        # Only the head and tail, which are not elements, have `None` pointers.
        assert node.before_me is not None
        assert node.after_me is not None

        # We assume, without checking, that `node` is actually part of the
        # linked list defined by `self.head` and `self.tail`.

        node.before_me.after_me = node.after_me
        node.after_me.before_me = node.before_me

    def add_node(self, node):
        before = self.tail.before_me

        before.after_me = node
        self.tail.before_me = node

        node.before_me = before
        node.after_me = self.tail

    def add_value(self, value):
        """Append a node having `value` and return the node."""
        node = LinkedList.Node(value)
        self.add_node(node)
        return node

    def pop_front(self):
        """Remove the first node and return the value it contained."""
        front_node = self.head.after_me
        self.remove_node(front_node)

        return front_node.value


def _lru_cache_key(args: tuple, kwargs: dict):
    # The python standard library version of lru_cache doesn't do this sorting,
    # so that in their case the order of keyword arguments matters.  Sorting
    # here seemed less tricky to me.
    kwargs_immutable = tuple(sorted(kwargs.items()))

    return args, kwargs_immutable


_lru_cache_not_found = object()


# only works for functions whose domain elements are immutable
def lru_cached(max_size):
    assert max_size > 0

    def cacheify(func):
        cache = {} # key => linked list node
        accesses = LinkedList() # front has least-recently-used

        def new_value(key):
            args, kwargs_immutable = key
            kwargs = dict(kwargs_immutable)

            value = func(*args, **kwargs)

            if len(cache) == max_size:
                lru_key, _ = accesses.pop_front()
                del cache[lru_key]

            # The "value" of the linked list node is the tuple `(key, value)`.
            # `value` is what we're caching, and `key` is there so we can
            # remove the corresponding item from `cache` should this node fall
            # off of the front.
            cache[key] = accesses.add_value((key, value))

            return value

        def cached_func(*args, **kwargs):
            key = _lru_cache_key(args, kwargs)
            node = cache.get(key, _lru_cache_not_found)

            if node is _lru_cache_not_found:
                return new_value(key)
            else:
                _, value = node.value
                return value

        return cached_func

    return cacheify


import time


@lru_cached(max_size=3)
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