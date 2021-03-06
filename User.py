#!/usr/bin/python3

from Kernel import Kernel, Flags, Memory

class UserSpace:
    '''
    Represents functions and operations available to a normal user.
    ''' 
    
    def __init__(self):
        self.kernel = Kernel()

    def write(self, file_descriptor, input, length, file='/proc/self/mem'):
        '''
        Write is a non-atomic operation meaning that it takes *multiple* steps
        to complete. 

        For the sake of this exercise we'll assume that write always calls
        mem_write. This is not (entirely) true and only applies IF you try to
        write to /proc/self/mem.
        
        What is /proc/self/mem? In short, it's a pseudo file (doesn't really
        exist on disk) that the kernel generates on the fly, this file represents
        the memory of our current program.

        Why /proc/self/mem? Recall that mem_write is only called when writing
        to /proc/self/mem, if you try to write to something else another internal
        write function is called. The bug that allows for the dirty cow exploit
        to exist occurs in the call stack of mem_write, this is why we try to
        write to /proc/self/mem/.

        FUN FACT: ptrace was an alternative attack vector to /proc/self/mem
        https://man7.org/linux/man-pages/man2/ptrace.2.html
        https://github.com/nowsecure/dirtycow/blob/master/ptrace.c

        For more context take a look at 
        http://lxr.linux.no/linux+v4.8/fs/proc/base.c#L933
        which defines operations for mem_write.

        Also the manual page for proc:
        https://man7.org/linux/man-pages/man5/procfs.5.html

        '''
        pass

if __name__ == '__main__':
    m = Memory()
    m.mmap("read_only.txt", Flags.READ_ONLY, Flags.PRIVATE)
    m.peek()
    print()
    m.memory[0].dirty = True
    m.memory[0].data = "test"
    m.sync()
    m.peek()