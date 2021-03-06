#-/usr/bin/python3

import time
import threading
from enum import Enum

class Flags(Enum):
    READ_ONLY = 1
    WRITE = 2
    COW = 3 # if someone tries to write, create a copy
    PRIVATE = 4 # anything marked private is writable

class vm_page:
    '''
    Represents a Virtual Memory (vm) page and also some functionality of a 
    page table

    Very roughly similar to 
    http://lxr.linux.no/linux+v4.8/include/linux/mm_types.h#L300
    '''
    def __init__(self, page_prot, data, file, offset, policy, evicted=False, dirty=False):
        self.page_prot = page_prot # page protection (READ ONLY)
        self.data = data # What this page actually holds
        self.file = file # The file that backs this page
        self.offset = offset # Offset in that file
        self.policy = policy # policy if someone tries to write to this page
        self.evicted = evicted # if this page is in memory or not
        self.dirty = dirty

    def sync(self):
        '''
        If this page is backed by a file, syncs any changes to this page to
        disk
        '''
        if self.dirty and self.file:
            with open(self.file, 'r+') as f:
                content = list(f.readlines()[0])
                f.seek(0)
                f.truncate
                # Seek to our offset and replace the data there
                i = self.offset
                for c in self.data:
                    if i < len(content):
                        content[i] = c
                    else:
                        break
                f.write("".join(content))
class Memory:
    '''
    Represents the Memory of the program (collection of pages)
    '''
    def __init__(self):
        self.memory = []

    def mmap(self, file, page_prot, policy):
        '''
        Maps a file into memory
        '''
        with open(file, 'r') as f:
            content = f.readlines()[0]
            for i in range(0, len(content), 4):
                data = ""
                for j in range(i, min(i+4, len(content))):
                    data += content[j]
                page = vm_page(page_prot, data, file, i, policy)
                self.memory.append(page)

    def peek(self):
        for page in self.memory:
            print(page.offset, page.data)

    def sync(self):
        '''
        Syncs any changes to pages that are backed by a file back to the hard
        disk
        '''
        for page in self.memory:
            page.sync()
class Kernel:
    '''
    Represents functions and operations in the Kernel

    This is really simplified and I combined the functionality of a lot of
    different kernel operations into a few functions for simplicity.
    ''' 

    def __init__(self):
        self.memory = Memory()

    def mem_write(self, buf):
        '''
        Special function that is called when writing to /proc/self/mem
        This function attempt to write to the memory location of the read only
        file and tries to handle any errors associate with that.
        
        http://lxr.linux.no/linux+v4.8/fs/proc/base.c#L903
        http://lxr.linux.no/linux+v4.8/fs/proc/base.c#L845
        '''
        
        # try to access memory 
            # try to write one page at a time

    def access_remote_vm(self, buf, write):
        '''
        Actual function that access or write to the virtual memory (vm)
        of our program.

        Recall from CSC369 that memory is divided into pages (4096 bytes). We
        are limited to getting 4096 bytes at a time.

        In this exercise we're limited to 4 characters at a time.

        http://lxr.linux.no/linux+v4.8/mm/memory.c#L3854
        '''
        # while not finish writing
        # get a page and write to it

    def __get_user_pages(self, gup_flags):
        '''
        Tries to find the page that we're looking for in memory, if
        not try to fault in the page.

        HINT: If the permission of the page and our request flag don't match
        we will also try to fault in the page by copying it (copy on write) so
        we can return a valid page

        :gup_flags (Get User Pages flags) encodes information about why the 
                    caller wants the page and what they intend to do with it

        http://lxr.linux.no/linux+v4.8/mm/gup.c#L519
        '''
        # try to get the page
        # if getting the page failed 
           # try to fault in the page
           # if it fails try again
           # yay we got a valid page

    def faultin_page(self):
        '''
        Tries to fault in the request page either to match requested permissions
        or load it from disk
        http://lxr.linux.no/linux+v4.8/mm/gup.c#L354
        '''
        # call handle mm fault to create new page or get it
        # remove write flag to prevent infinite loop

    def handle_mm_fault(self):
        '''
        http://lxr.linux.no/linux+v4.8/mm/memory.c#L3566
        '''
        # Get page and return it
        pass
