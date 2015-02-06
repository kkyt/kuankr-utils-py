import os
from time import time

class Snowflake(object):
    def __init__(self, worker_id=None):
        if worker_id is None:
            worker_id = int(os.environ.get('SNOWFLAKE_WORKER_ID', 0))

        self.max_time = int(time() * 1000)
        self.sequence = 0

        #self.epoch = 1259193600000 # 2009-11-26
        #self.time_shift_bits = 22
        #self.max_worker_id = 1024

        self.epoch = 0
        self.time_shift_bits = 20
        self.worker_shift_bits = 12
        self.max_worker_id = 256

        self.max_sequence = 2**self.worker_shift_bits

        if not (worker_id>=0 and worker_id<self.max_worker_id):
            raise Exception('worker_id should >=0 and < %s, got %r' % (self.max_worker_id, worker_id))

        self.worker_id = worker_id
    
    def next(self):
        curr_time = int(time() * 1000)
        
        if curr_time < self.max_time:
            raise Exception('Clock went backwards! %d < %d' % (curr_time, self.max_time))
        
        if curr_time > self.max_time:
            self.sequence = 0
            self.max_time = curr_time
        
        self.sequence += 1
        if self.sequence >= self.max_sequence:
            raise Exception('Sequence Overflow: %d' % self.sequence)
        
        id = ((curr_time-self.epoch)<<self.time_shift_bits) + (self.worker_id<<self.worker_shift_bits) + self.sequence
        return id


