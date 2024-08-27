"""
CS472 Project 1 - MIPS Disassembler
Michael Kwok
June 18, 2024
"""

import numpy as np


# =============================================================================
# ================================= CONSTANTS =================================
# =============================================================================

INSTRUCT_DICT = {0x20: 'add', 0x22: 'sub', 0x24: 'and', 0x25: 'or', 
                    0x2a: 'slt', 0x23: 'lw', 0x2b: 'sw', 0x4: 'beq',
                    0x5: 'bne'}

OPCODE_MASK = 0xFC000000
OPCODE_SHIFT = 26
R_FMT_MASKS = [0x3E00000, 0x1F0000, 0xF800, 0x7C0, 0x3F]
R_FMT_SHIFTS = [21, 16, 11, 6, 0]
I_FMT_MASKS = [0x3E00000, 0x1F0000, 0xFFFF]
I_FMT_SHIFTS = [21, 16, 0]


# =============================================================================
# ================================= FUNCTION ==================================
# =============================================================================

def decode_instruction(instruct, instruct_address):
    
    # decide format
    opcode = (instruct & OPCODE_MASK) >> OPCODE_SHIFT
    if opcode == 0:
        fmt = 'R'
    else:
        fmt = 'I'
    
    # R format
    if fmt == 'R':
        src_1 = (instruct & R_FMT_MASKS[0]) >> R_FMT_SHIFTS[0]
        src_2 = (instruct & R_FMT_MASKS[1]) >> R_FMT_SHIFTS[1]
        dest = (instruct & R_FMT_MASKS[2]) >> R_FMT_SHIFTS[2]
        assert instruct & R_FMT_MASKS[3] == 0  # shamt is assumed to be 0
        func = INSTRUCT_DICT[(instruct & R_FMT_MASKS[4]) >> R_FMT_SHIFTS[4]]
        decoded_instruct = f'{func} ${dest}, ${src_1}, ${src_2}'
        
    # I format
    elif fmt == 'I':
        func = INSTRUCT_DICT[opcode]
        src_1 = (instruct & I_FMT_MASKS[0]) >> I_FMT_SHIFTS[0]
        src_2_dest = (instruct & I_FMT_MASKS[1]) >> I_FMT_SHIFTS[1]
        const_offset = np.short((instruct & I_FMT_MASKS[2]) >> I_FMT_SHIFTS[2])
        
        # load and store
        if func == 'lw' or func == 'sw':
            decoded_instruct = f'{func} ${src_2_dest}, {const_offset}(${src_1})'
        
        # branches
        elif func == 'beq' or func == 'bne':
            const_offset = (const_offset << 2) + 4
            address = hex(instruct_address + const_offset)
            decoded_instruct = f'{func} ${src_1}, ${src_2_dest}, address {address}'
        
    return decoded_instruct


# =============================================================================
# ============================== INPUT & DECODE ===============================
# =============================================================================

instructions = [0x032BA020, 0x8CE90014, 0x12A90003, 0x022DA822, 
                0xADB30020, 0x02697824, 0xAE8FFFF4, 0x018C6020, 
                0x02A4A825, 0x158FFFF7, 0x8ECDFFF0]

# starting address
instruct_address = 0x9A040

for instruct in instructions:
    decoded_instruct = decode_instruction(instruct, instruct_address)
    print(hex(instruct_address), decoded_instruct)
    instruct_address += 4

