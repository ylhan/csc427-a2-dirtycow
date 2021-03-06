#-/usr/bin/python3

import time
import threading
from enum import Enum

class Flags(Enum):
    READ_ONLY = 1
    WRITE = 2
    COW = 3 # if someone tries to write, create a copy
    PRIVATE = 4 # this file is writable
    MAP_PRIVATE = 5 # Flag for mmap

class vm_page:
    '''
    Represents a Virtual Memory (vm) page and also some functionality of a 
    page table

    Very roughly similar to 
    http://lxr.linux.no/linux+v4.8/include/linux/mm_types.h#L300
    '''
    def __init__(self, page_prot, data, file, offset, policy, dirty=False):
        self.page_prot = page_prot # page protection (READ ONLY)
        self.data = data # What this page actually holds
        self.file = file # The file that backs this page
        self.offset = offset # Offset in that file
        self.policy = policy # policy if someone tries to write to this page
        self.dirty = dirty # if this page is dirty or not

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
                    i += 1
                f.write("".join(content))

    def copy_on_write(self):
        '''
        This is a lie. This much more complicated in the real kernel and 
        vm_page would just be a struct. 

        This function copies this page and returns a copied page with no
        file backing and policy set to private (indicates that it's copied).
        '''
        return vm_page(self.page_prot, self.data, None, (-self.offset)-1, Flags.PRIVATE)
    
    def write(self, data):
        '''
        Writes to this page. Again this isn't usually located here but I put it
        here for simplicity.
        '''
        self.data = data
        self.dirty = True

class Memory:
    '''
    Represents the Memory of the program (collection of pages)
    '''
    def __init__(self):
        self.memory = dict()

    def mmap(self, file, page_prot, policy):
        '''
        Maps a file into memory
        '''
        self.file = file
        self.page_prot = page_prot
        self.policy = policy
        with open(file, 'r') as f:
            content = f.readlines()[0]
            for i in range(0, len(content), 4):
                data = ""
                for j in range(i, min(i+4, len(content))):
                    data += content[j]
                page = vm_page(page_prot, data, file, i, policy)
                if policy == Flags.MAP_PRIVATE:
                    page.policy = Flags.COW
                self.memory[i] = page

    def peek(self):
        for k in sorted(self.memory.keys()):
            page = self.memory[k]
            # print(page.offset, page.data, page.page_prot, page.file,page.policy, page.dirty)
            print(page.offset, page.data)

    def sync(self):
        '''
        Syncs any changes to pages that are backed by a file back to the hard
        disk
        '''
        for k in sorted(self.memory.keys()):
            page = self.memory[k]
            page.sync()

    def reload_page(self, offset):
        if offset < 0:
            offset = -(offset + 1)
            
        with open(self.file, 'r') as f:
            content = f.readlines()[0]
            page = vm_page(self.page_prot, content[offset:offset+4], self.file, offset, self.policy)
            if self.policy == Flags.MAP_PRIVATE:
                page.policy = Flags.COW
            self.memory[offset] = page
            self.memory[-offset -1] = page.copy_on_write()

    def __contains__(self, item):
        return item in self.memory

    def __getitem__(self, key):
        return self.memory[key]

    def __setitem__(self, key, value):
        self.memory[key] = value

    def clear(self):
        self.memory = dict()
class Kernel:
    '''
    Represents functions and operations in the Kernel

    This is really simplified and I combined the functionality of a lot of
    different kernel operations into a few functions for simplicity.
    ''' 

    def __init__(self):
        self.memory = Memory()

    def scheduler(self, code):
        EXECUTE = None # Replace this
        if code == EXECUTE:
            self.madvise()

    def mem_write(self, buf, offset):
        '''
        Special function that is called when writing to /proc/self/mem
        This function attempt to write to the memory location of the read only
        file and tries to handle any errors associate with that.
        
        http://lxr.linux.no/linux+v4.8/fs/proc/base.c#L903
        http://lxr.linux.no/linux+v4.8/fs/proc/base.c#L845
        '''
        # Normally this function does some checks and sets up some buffers & structs
        # but I removed that for simplicity
        self.scheduler(1) # INTERUPT
        self.access_remote_vm(buf, offset, True)

    def access_remote_vm(self, buf, offset, write):
        '''
        Actual function that access or write to the virtual memory (vm)
        of our program.

        Recall from CSC369 that memory is divided into pages (4096 bytes). We
        are limited to getting 4096 bytes at a time.

        In this exercise we're limited to 4 characters at a time to simulate this.

        http://lxr.linux.no/linux+v4.8/mm/memory.c#L3854
        '''
        self.scheduler(2) # INTERUPT
        for i in range(offset, len(buf), 4):
            if write:
                page = self.__get_user_pages([Flags.WRITE], i)
                page.write(buf[i:i+4])
                self.memory.sync()
            self.scheduler(3) # INTERUPT

    def __get_user_pages(self, gup_flags, offset):
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
        ret = offset
        page = None
        while not page:
            if ret < 0:
                self.scheduler(4) # INTERUPT
            page = self.follow_page_mask(gup_flags,ret)
            # self.memory.peek()
            if not page:
                ret = self.faultin_page(gup_flags, offset)
        
        return page

    def faultin_page(self, flags, offset):
        '''
        Tries to fault in the request page either to match requested permissions
        or load it from disk
        http://lxr.linux.no/linux+v4.8/mm/gup.c#L354
        '''
        # call handle mm fault to create new page or get it
        # remove write flag to prevent infinite loop
        self.scheduler(5) # INTERUPT
        ret = self.handle_mm_fault(flags, offset)
        self.scheduler(6) # INTERUPT
        if ret and offset in self.memory and len(flags) and flags[0] == Flags.WRITE:
            flags.pop(0)
        return ret

    def handle_mm_fault(self, flags, offset):
        '''
        Handles the fault and resolves it by either copying the page
        or bringing it back from disk

        http://lxr.linux.no/linux+v4.8/mm/memory.c#L3566
        '''
        # Get page, deal with issues and return it
        self.scheduler(7) # INTERUPT
        ret = offset
        if offset not in self.memory:
            self.memory.reload_page(offset)
        page = self.memory[offset]
        if len(flags) and page.policy == Flags.COW:
            n_page = page.copy_on_write()
            ret = (-offset) - 1
            self.memory[ret] = n_page
        self.scheduler(8) # INTERUPT
        return ret

    def follow_page_mask(self, flags, offset):
        '''
        Tries to get the requested page, fails if permissions don't match
        or if page is not in memory

        http://lxr.linux.no/linux+v4.8/mm/gup.c#L214
        '''
        if offset is None:
            return None 

        if offset in self.memory:
            page_prot =  self.memory[offset].page_prot
            if page_prot == Flags.READ_ONLY:
                if Flags.WRITE in flags:
                    return None
            return self.memory[offset]    
        return None

    def madvise(self):
        '''
        Clears memory 
        '''
        self.memory.clear()