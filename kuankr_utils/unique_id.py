import os
from time import time

class Snowflake(object):
    def __init__(self, worker_id=None):
        if worker_id is None:
            worker_id = int(os.environ.get('SNOWFLAKE_WORKER_ID', 0))
        if not isinstance(worker_id, int) and worker_id>=0 and worker_id<1024:
            raise Exception('worker_id should >=0 and < 1024, got %r' % worker_id)
        self.worker_id = worker_id

        self.max_time = int(time() * 1000)
        self.sequence = 0
        self.epoch = 1259193600000 # 2009-11-26
    
    def next(self):
        curr_time = int(time() * 1000)
        
        if curr_time < self.max_time:
            raise Exception('Clock went backwards! %d < %d' % (curr_time, self.max_time))
        
        if curr_time > self.max_time:
            self.sequence = 0
            self.max_time = curr_time
        
        self.sequence += 1
        if self.sequence > 4095:
            raise Exception('Sequence Overflow: %d' % self.sequence)
        
        id = ((curr_time - self.epoch) << 22) + (self.worker_id << 12) + self.sequence
        return id


