import gevent
import gevent.queue

def stream_to_queue(s, q=None, **kwargs):
    if q is None:
        q = gevent.queue.Queue(**kwargs)
    for x in s:
        q.put(x)
    q.put(StopIteration)
    return q

def queue_to_stream(q):
    return iter(q)

