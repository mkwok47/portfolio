"""
CS472 Project 2 - Cache Simulation
Michael Kwok
July 9, 2024
"""

import pandas as pd


# =============================================================================
# =============================== SLOT / CACHE ================================
# =============================================================================

# number of slots in a cache
NUM_SLOTS = 16

class Slot():
    
    def __init__(self, slot):
        self.slot = slot
        self.valid = 0
        self.tag = 0
        self.dirty = 0
        self.data = [0 for i in range(0xf)]
        
    def __str__(self):
        return (f'Slot {self.slot} with valid bit {self.valid}, dirty bit'
                f'{self.dirty}, tag {self.tag}, data {self.data}')

def display_cache(cache):
    
    # utilize pandas dataframe
    cache_df = pd.DataFrame(columns=['slot', 'valid', 'tag', 'dirty', 'data'])
    
    for slot in cache:
        cache_df.at[slot.slot, 'slot'] = hex(slot.slot)[2:]
        cache_df.at[slot.slot, 'valid'] = slot.valid
        cache_df.at[slot.slot, 'tag'] = hex(slot.tag)[2:]
        cache_df.at[slot.slot, 'dirty'] = slot.dirty
        
        slot_data_hex = [hex(x)[2:] for x in slot.data]
        cache_df.at[slot.slot, 'data'] = ' '.join(slot_data_hex)
        
    print(cache_df.to_string(index=False))

# initialize cache
cache = [Slot(i) for i in range(NUM_SLOTS)]        


# =============================================================================
# ================================ MAIN MEMORY ================================
# =============================================================================

MAX_MEM_ADDR = 0x7ff

# initialize main memory
main_mem = [i % 256 for i in range(MAX_MEM_ADDR)]


# =============================================================================
# =============================== FUNCTIONALITY ===============================
# =============================================================================

BLOCK_OFFSET_MASK = 0b1111

SLOT_NUM_MASK = 0b11110000
SLOT_NUM_SHIFT = 4

TAG_MASK = 0b111100000000
TAG_SHIFT = 8

# handles read, write, display
def execute_instruction(address, request, write_data=None):
        
    # apply masks and shifts to extract elements
    block_offset = address & BLOCK_OFFSET_MASK
    slot_num = (address & SLOT_NUM_MASK) >> SLOT_NUM_SHIFT
    tag = (address & TAG_MASK) >> TAG_SHIFT
        
    # read
    if request == 'R':
        
        # cache hit
        if cache[slot_num].valid == 1 and cache[slot_num].tag == tag:
            block = cache[slot_num].data
            data = block[block_offset]
            print(f'At address {hex(address)}, there is the value {hex(data)} (Cache Hit)')
            
        # cache miss
        else:
            
            # write-back cache: copy current block to main memory if dirty
            if cache[slot_num].dirty == 1:
                block_start = (cache[slot_num].tag << 8) + \
                              (cache[slot_num].slot << 4)
                main_mem[block_start:block_start+0xf+1] = cache[slot_num].data
                
                # reset dirty bit
                cache[slot_num].dirty = 0
                
            # obtain new block from main memory
            block_start = address - block_offset
            block = main_mem[block_start:block_start+0xf+1]
            
            # copy over block to cache (overwrite)
            cache[slot_num].data = block
            
            # obtain requested address's data
            data = block[block_offset]
            print(f'At address {hex(address)}, there is the value {hex(data)} (Cache Miss)')
            
            # update attributes
            cache[slot_num].valid = 1
            cache[slot_num].tag = tag
    
    # write
    elif request == 'W':
        
        # cache hit
        if cache[slot_num].valid == 1 and cache[slot_num].tag == tag:
            
            # write-back cache: update only the cache, not main memory
            cache[slot_num].data[block_offset] = write_data
            
            # update attributes
            cache[slot_num].dirty = 1
            print(f'The value {hex(write_data)} has been written to address '
                  f'{hex(address)} (Cache Hit)')
            
        # cache miss
        else:
            
            # write-back cache: copy current block to main memory if dirty
            if cache[slot_num].dirty == 1:
                block_start = (cache[slot_num].tag << 8) + \
                              (cache[slot_num].slot << 4)
                main_mem[block_start:block_start+0xf+1] = cache[slot_num].data
                
                # reset dirty bit
                cache[slot_num].dirty = 0
            
            # write new data to main memory
            main_mem[address] = write_data
            
            # bring in clean copy from main memory to cache
            block_start = address - block_offset
            block = main_mem[block_start:block_start+0xf+1]
            cache[slot_num].data = block
            print(f'The value {hex(write_data)} has been written to address '
                  f'{hex(address)} (Cache Miss)')
            
            # update attributes
            cache[slot_num].valid = 1
            cache[slot_num].tag = tag
        
    # display
    elif request == 'D':
        display_cache(cache)
        
    
# =============================================================================
# ================================== PROGRAM ==================================
# =============================================================================

file = 'input.txt'

# intake and execute instructions
with open(file, 'r') as f:
    
    instructions = [x.strip() for x in f.readlines()]
    
    # convert string to hex
    requests = ['R', 'W', 'D']
    instructions = [int(x, base=16) if x not in requests else x 
                    for x in instructions]
    
    for i in range(len(instructions)):
        request = instructions[i]
        
        # read
        if request == 'R':
            address = instructions[i+1]
            execute_instruction(address, request)
            
        # write
        elif request == 'W':
            address = instructions[i+1]
            data = instructions[i+2]
            execute_instruction(address, request, data)
            
        # display
        elif request == 'D':
            execute_instruction(address, request)
            
