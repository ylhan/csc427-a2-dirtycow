#!/usr/bin/python3

from Kernel import kernel

class User: 
    
    def __init__(self):
        self.kernel = Kernel()

    def write(self, file_descriptor, input, length):
        '''
        Write doesn't actually write to memory directly instead under the hood
        it actually calls a 
        '''
        pass

    def open(self, file):
        self.kernel.load(file)

    def mmap(self, file, memory_region, flag):
        self.kernel.mmap(file, memory_region, flag)