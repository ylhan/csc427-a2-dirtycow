#-/usr/bin/python3

import time
import threading
from enum import Enum

class Permissions(Enum):
    READ_ONLY = 1
    FOLL_WRITE = 2

class vm_area_struct:
    '''
    http://lxr.linux.no/linux+v4.8/include/linux/mm_types.h#L300 

    This struct defines a memory VMM memory area. There is one of these
    per VM-area/task.  A VM area is any part of the process virtual memory
    space that has a special rule for the page-fault handlers (ie a shared
    library, the executable area etc).
    '''
    def __init__(self):
        vm_file = vm_file # File backing this mapping
        vm_prot = PERMISSIONS.READ_ONLY# Abstraction/similar to vm_page_prot

class Kernel:
    
    def __init__(self):
        with open(f, 'r') as file:
            self._memory = list(file.read())
            self._root_mem_bound = len(self._memory)
            self._memory.extend(['u']*(self._root_mem_bound))
        self._file = f
        self._write_pointer = 0
        self.lock = threading.Lock()

    def os_scheduler(self):
        ''' TODO: Pseudo Randomly schedules execution and simulate the CPU
        '''
        pass

    def lru_cache_eviction(self):
        ''' TODO: write the eviction policy for least recently used page
        evicted pages MUST
        '''
        pass

    def semaphore_lock(self, conditional):
        ''' TODO: Implement a semaphore that locks and unlocks based on a conditional
        '''
        pass

    def semaphore_unlock(self, conditional):
        ''' TODO: Implement a semaphore that locks and unlocks based on a conditional
        '''
        pass

    def _write(self, buffer):
        j = 0
        for i in range(self._write_pointer, self._write_pointer+len(buffer)):
            self._memory[i] = buffer[j]
            j += 1

    def _copy_on_write(self, addr, buffer):
        self._write_pointer = addr+self._root_mem_bound
        self._memory[self._root_mem_bound:]= self._memory[:self._root_mem_bound]
        self._write(buffer)

    def dontneed(self, addr, length):
        self.lock.acquire()
        self._write_pointer = int(addr, 16)
        # Write back to disk
        if self._write_pointer < 0:
            raise AddressError("You can't write to a negative address.")

        if self._write_pointer >= len(self._memory):
            raise AddressError(f"The address you are trying to write to is >= {len(self._memory)} (size of memory).")

        if self._write_pointer >= self._root_mem_bound:
            print("No write permissions to rootfile discarding memory...")
            self._memory[self._root_mem_bound:] = ['u']*(self._root_mem_bound)
            return

        if self._write_pointer < self._root_mem_bound and self._write_pointer + length > self._root_mem_bound:
            raise AddressError("Length too long. No write permissions to rootfile discarding memory...")
        
        with open(self._file, 'w') as file:
            out = "".join(self._memory[self._write_pointer:self._write_pointer+length])
            file.write(out)
        self.lock.release()

    def peek(self, col=8):
        if col <= 0:
            print(f"Provided columns per row must be > 0")
            return

        print(f"Read only bounds: {0:08x}...{self._root_mem_bound-1:08x}")
        print(f"Free bounds:      {self._root_mem_bound-1:08x}...{len(self._memory)-1:08x}")
        print("=== Memory ===")
        for i in range(0, len(self._memory), col):
            out = f"0x{i:08x}: "
            for j in range(i, min(i+col, len(self._memory))):
                out += f" {self._memory[j]}"
            print(out)

    def load(self, file):
        '''
        This is an abstraction

        The proc filesystem is a pseudo-filesystem which provides an
        interface to kernel data structures.  It is commonly mounted at
        /proc.  Typically, it is mounted automatically by the system, but
        it can also be mounted manually using a command such as:

            mount -t proc proc /proc

        Most of the files in the proc filesystem are read-only, but some
        files are writable, allowing kernel variables to be changed.
        '''

    def handle_mem_swap(self, buffer):
        addr = int(addr, 16)
        if addr < 0:
            raise AddressError("You can't write to a negative address.")

        if addr >= len(self._memory):
            raise AddressError(f"The address you are trying to write to is >= {len(self._memory)} (size of memory).")

        if addr >= self._root_mem_bound and len(buffer) > (len(self._memory)-addr):
            raise MemoryError(f"Your buffer is too large to fit in memory at your given address.")

        if addr < self._root_mem_bound and len(buffer) > (self._root_mem_bound-addr):
            raise MemoryError(f"Your buffer is too large to fit in memory at your given address.")

        # Write to user memory
        if addr >= self._root_mem_bound:
            self._write(addr, buffer)
        
        # Writing to root memory: copy on write
        if addr < self._root_mem_bound:
            self._copy_on_write(addr, buffer)

    def __access_remote_vm(self, task_struct):
        ''' Access another process' address space as given in mm.  If non-NULL, use the
            given task for page fault accounting.
            https://code.woboq.org/linux/linux/mm/memory.c.html#__access_remote_vm
        '''
        vm_area_struct = None
        old_buf = None 
        write = gup_flags & Permissions.FOLL_WRITE
        down_read(mmmmap_sem)
        # ignore errors, just check how much was successfully transferred */
        while (_len):
            maddr
            page = None
            ret = get_user_pages_remote(tsk, mm, addr, 1,gup_flags, page, vma, NULL)
            if (ret <= 0):
            #ifndef CONFIG_HAVE_IOREMAP_PROT
                break
            #else
                vma = find_vma(mm, addr)
                if (not vma or vma.vm_start > addr):
                    break
                if (vma.vm_ops and vma.vm_ops.access):
                    ret = vma.vm_ops.access(vma, addr, buf,
                                len, write)
                if (ret <= 0):
                    break
                bytes = ret
            #endif
            else:
                bytes = len
                offset = addr & (PAGE_SIZE-1)
                if (bytes > PAGE_SIZE-offset):
                    bytes = PAGE_SIZE-offset
                maddr = kmap(page)
                if (write):
                    copy_to_user_page(vma, page, addr,
                            maddr + offset, buf, bytes)
                    set_page_dirty_lock(page)
                else :
                    copy_from_user_page(vma, page, addr, buf, maddr + offset, bytes)
                kunmap(page)
                put_page(page)
            len -= bytes
            buf += bytes
            addr += bytes
        up_read(mm.mmap_sem)
        return buf - old_buf

    def __get_user_pages(tsk, mm,start, nr_pages, gup_flags, pages, vmas, nonblocking):
        '''
        __get_user_pages() - pin user pages in memory
        @tsk:        task_struct of target task
        @mm:         mm_struct of target mm
        @start:      starting user address
        @nr_pages:   number of pages from start to pin
        @gup_flags:  flags modifying pin behaviour
        @pages:      array that receives pointers to the pages pinned.
                    Should be at least nr_pages long. Or NULL, if caller
                    only intends to ensure the pages are faulted in.
        @vmas:       array of pointers to vmas corresponding to each page.
                    Or NULL if the caller does not require them.
        @nonblocking: whether waiting for disk IO or mmap_sem contention
        Returns number of pages pinned. This may be fewer than the number
        requested. If nr_pages is 0 or negative, returns 0. If no pages
        were pinned, returns -errno. Each page returned must be released
        with a put_page() call when it is finished with. vmas will only
        remain valid while mmap_sem is held.
        Must be called with mmap_sem held.
        http://lxr.linux.no/linux+v4.8/mm/gup.c#L519 
        '''
        i = 0
        page_mask = Nopne
        vma = None

        if (not nr_pages):
            return 0

        VM_BUG_ON(-pages != - (gup_flags & FOLL_GET))

        while True:
            if (-vma or start >= vma.vm_end) :
                vma = find_extend_vma(mm, start)
                if (-vma and in_gate_area(mm, start)):
                    ret = get_gate_page(mm, start & PAGE_MASK,gup_flags, vma, pages)
                    if (ret):
                        return i
                    page_mask = 0

                if (-vma or check_vma_flags(vma, gup_flags)):
                        return -EFAULT
                if (is_vm_hugetlb_page(vma)):
                        i = follow_hugetlb_page(mm, vma, pages, vmas,)
                        continue


            if (unlikely(fatal_signal_pending(current))):
                    return i
            cond_resched()
            page = follow_page_mask(vma, start, foll_flags, page_mask)
    
            if (vmas):
                vmas[i] = vma
                page_mask = 0
            page_increm = 1 + (~(start >> PAGE_SHIFT) & page_mask)
            i += page_increm
            start += page_increm * PAGE_SIZE
            nr_pages -= page_increm
        return i


    def __faultin_page(tsk, vma, address, flags, nonblocking):
        '''
        mmap_sem must be held on entry.  If @nonblocking != NULL and
       @flags does not include FOLL_NOWAIT, the mmap_sem may be released.
        If it is, *@nonblocking will be set to 0 and -EBUSY returned.
        http://lxr.linux.no/linux+v4.8/mm/gup.c#L519 
        '''
        i = 0
        page_mask = None
        vma = None

        if (not nr_pages):
            return 0

        VM_BUG_ON(-pages != - (gup_flags & FOLL_GET))

        if (-vma or start >= vma.vm_end) :
            vma = find_extend_vma(mm, start)
            if (-vma and in_gate_area(mm, start)):
                ret = get_gate_page(mm, start & PAGE_MASK,gup_flags, vma, pages)
                if (ret):
                    return i
                page_mask = 0
        if (vmas):
            vmas[i] = vma
            page_mask = 0
        page_increm = 1 + (~(start >> PAGE_SHIFT) & page_mask)
        i += page_increm
        start += page_increm * PAGE_SIZE
        nr_pages -= page_increm

        if (-vma or check_vma_flags(vma, gup_flags)):
                    return -EFAULT
        if (is_vm_hugetlb_page(vma)):
                i = follow_hugetlb_page(mm, vma, pages, vmas)

        return i
class MemoryError(Exception):
    def __init__(self, message):
        super().__init__(message)

class AddressError(Exception):
    def __init__(self, message):
        super().__init__(message)