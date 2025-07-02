"""
CS472 Project 3 - Pipeline Simulation
Michael Kwok
July 30, 2024

Simulating pipeline registers (IF=instruction fetch, ID=instruction decode,
EX=execute, MEM=memory, WB=writeback)

Please note that the following are omitted for simplification since there are
no branches in the given instruction set: Branch control signal, 
ID_EX_pipeline.IncrPC, EX_MEM_pipeline.CalcBTA, EX_MEM_pipeline.Zero
"""

from copy import deepcopy
import numpy as np

# =============================================================================
# =============================== FUNCTIONALITY ===============================
# =============================================================================

# codes
OPCODE_DICT = {0x20: 'lb', 0x28: 'sb'}
FUNC_CODE_DICT = {0x20: 'add', 0x22: 'sub', 0: 'nop'}
ALU_OP_DICT = {'add': 0b10, 'sub': 0b10, 'lb': 0b00, 'sb': 0b00, 'nop': None}

# shifts and masks
OPCODE_MASK = 0xFC000000
OPCODE_SHIFT = 26
R_FMT_MASKS = [0x3E00000, 0x1F0000, 0xF800, 0x7C0, 0x3F]
R_FMT_SHIFTS = [21, 16, 11, 6, 0]
I_FMT_MASKS = [0x3E00000, 0x1F0000, 0xFFFF]
I_FMT_SHIFTS = [21, 16, 0]

# pipeline classes
class IF_ID_pipeline:
    def __init__(self, instruction):
        self.instruction = instruction
    def __str__(self):
        return f'Inst: {hex(self.instruction)}'
        
class ID_EX_pipeline:
    def __init__(self, RegDst, ALUSrc, ALUOp, MemRead, MemWrite, MemToReg, 
                 RegWrite, read_data_1, read_data_2, SEOffset, Wreg_20_16, 
                 Wreg_15_11, func):
        self.RegDst = RegDst
        self.ALUSrc = ALUSrc
        self.ALUOp = ALUOp
        self.MemRead = MemRead
        self.MemWrite = MemWrite
        self.MemToReg = MemToReg
        self.RegWrite = RegWrite
        
        self.read_data_1 = read_data_1
        self.read_data_2 = read_data_2
        self.SEOffset = SEOffset
        self.Wreg_20_16 = Wreg_20_16
        self.Wreg_15_11 = Wreg_15_11
        self.func = func
    def __str__(self):
        return f'''Control: RegDst={self.RegDst}, ALUSrc={self.ALUSrc}, 
ALUOp={bin(self.ALUOp)}, MemRead={self.MemRead}, MemWrite={self.MemWrite}, 
MemToReg={self.MemToReg}, RegWrite={self.RegWrite}
            
ReadReg1Value = {hex(self.read_data_1)} ReadReg2Value = {hex(self.read_data_2)}
SEOffset = {hex(self.SEOffset & 0xffffffff)} WriteReg_20_16 = {self.Wreg_20_16}
WriteReg_15_11 = {self.Wreg_15_11} Function = {hex(self.func)}
'''
        
class EX_MEM_pipeline:
    def __init__(self, MemRead, MemWrite, MemToReg, RegWrite, ALUResult, 
                 SwValue, WriteRegNum):
        self.MemRead = MemRead
        self.MemWrite = MemWrite
        self.MemToReg = MemToReg
        self.RegWrite = RegWrite
        
        self.ALUResult = ALUResult
        self.SwValue = SwValue
        self.WriteRegNum = WriteRegNum
    def __str__(self):
        return f'''Control: MemRead={self.MemRead}, MemWrite={self.MemWrite}, 
MemToReg={self.MemToReg}, RegWrite={self.RegWrite}

ALUResult = {hex(self.ALUResult)} SwValue = {hex(self.SwValue)} 
WriteRegNum = {self.WriteRegNum}
    '''
        
class MEM_WB_pipeline:
    def __init__(self, MemToReg, RegWrite, LWDataValue, ALUResult, WriteRegNum):
        self.MemToReg = MemToReg
        self.RegWrite = RegWrite
        
        self.LWDataValue = LWDataValue
        self.ALUResult = ALUResult
        self.WriteRegNum = WriteRegNum
    def __str__(self):
        return f'''Control: MemToReg={self.MemToReg}, RegWrite={self.RegWrite}

LWDataValue = {hex(self.LWDataValue)} ALUResult = {hex(self.ALUResult)} 
WriteRegNum = {self.WriteRegNum}
    '''

# pipeline methods
def IF_stage():
    global IF_ID_Write
    instruction = InstructionCache[clock_cycle_num-1]
    IF_ID_Write.instruction = instruction

def ID_stage():
    global ID_EX_Write, RegDst, ALUSrc, ALUOp, MemRead, MemWrite, MemToReg, RegWrite
    instruct = IF_ID_Read.instruction
    if instruct == 0:
        ID_EX_Write = ID_EX_pipeline(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        return
    
    r_src_1 = (instruct & R_FMT_MASKS[0]) >> R_FMT_SHIFTS[0]
    r_src_2 = (instruct & R_FMT_MASKS[1]) >> R_FMT_SHIFTS[1]
    r_dest = (instruct & R_FMT_MASKS[2]) >> R_FMT_SHIFTS[2]
    i_const_offset = np.short((instruct & I_FMT_MASKS[2]) >> I_FMT_SHIFTS[2])
    
    # decide R vs I format
    opcode = (instruct & OPCODE_MASK) >> OPCODE_SHIFT
    r_func = (instruct & R_FMT_MASKS[4]) >> R_FMT_SHIFTS[4]
    
    # R fmt
    if opcode == 0:
        # set control signals
        RegDst = 1
        ALUSrc = 0
        ALUOp = ALU_OP_DICT[FUNC_CODE_DICT[r_func]]
        MemRead = 0
        MemWrite = 0
        MemToReg = 0
        RegWrite = 1
        
    # I fmt
    else:
        # decide load vs store
        i_func = OPCODE_DICT[opcode]
        
        # load
        if i_func == 'lb':
            # set control signals
            RegDst = 0
            ALUSrc = 1
            ALUOp = ALU_OP_DICT[i_func]
            MemRead = 1
            MemWrite = 0
            MemToReg = 1
            RegWrite = 1
                
        # store
        elif i_func == 'sb':
            # set control signals
            RegDst = 0 # None
            ALUSrc = 1
            ALUOp = ALU_OP_DICT[i_func]
            MemRead = 0
            MemWrite = 1
            MemToReg = 0 # None
            RegWrite = 0
            
        else:
            raise ValueError('Unexpected format')

    # update ID/EX Write pipeline
    read_data_1 = Regs[r_src_1]
    read_data_2 = Regs[r_src_2]
    SEOffset = np.int32(i_const_offset)
    Wreg_20_16 = r_src_2
    Wreg_15_11 = r_dest
    ID_EX_Write = ID_EX_pipeline(RegDst, ALUSrc, ALUOp, MemRead, MemWrite, 
                                 MemToReg, RegWrite, read_data_1, read_data_2, 
                                 SEOffset, Wreg_20_16, Wreg_15_11, r_func)

def EX_stage():
    global EX_MEM_Write
    
    # set WriteRegNum based on RegDst control signal
    if ID_EX_Read.RegDst == 0:
        WriteRegNum = ID_EX_Read.Wreg_20_16
    elif ID_EX_Read.RegDst == 1:
        WriteRegNum = ID_EX_Read.Wreg_15_11

    # set ALUResult operand based on ALUSrc control signal
    if ID_EX_Read.ALUSrc == 0:
        operand = ID_EX_Read.read_data_2
    elif ID_EX_Read.ALUSrc == 1:
        operand = ID_EX_Read.SEOffset
    
    # lb and sb ALU execution
    if ID_EX_Read.ALUOp == 0b00:
        ALUResult = ID_EX_Read.read_data_1 + operand
        
    # r-type ALU execution
    elif ID_EX_Read.ALUOp == 0b10:
        if ID_EX_Read.func == 0x20:
            ALUResult = ID_EX_Read.read_data_1 + operand
        elif ID_EX_Read.func == 0x22:
            ALUResult = ID_EX_Read.read_data_1 - operand
        
    SwValue = ID_EX_Read.read_data_2

    # update EX/MEM Write pipeline
    EX_MEM_Write = EX_MEM_pipeline(ID_EX_Read.MemRead, ID_EX_Read.MemWrite, 
                                   ID_EX_Read.MemToReg, ID_EX_Read.RegWrite, 
                                   ALUResult, SwValue, WriteRegNum)

def MEM_stage():
    global MEM_WB_Write
    
    LWDataValue = 0
    if EX_MEM_Read.MemRead:
        LWDataValue = Main_Mem[EX_MEM_Read.ALUResult]
    if EX_MEM_Read.MemWrite:
        Main_Mem[EX_MEM_Read.ALUResult] = EX_MEM_Read.SwValue % 256
    
    # update MEM/WB Write pipeline
    MEM_WB_Write = MEM_WB_pipeline(EX_MEM_Read.MemToReg, EX_MEM_Read.RegWrite,
                                   LWDataValue, EX_MEM_Read.ALUResult, 
                                   EX_MEM_Read.WriteRegNum)

def WB_stage():
    if MEM_WB_Read.RegWrite:
        if MEM_WB_Read.MemToReg:
            Regs[MEM_WB_Read.WriteRegNum] = MEM_WB_Read.LWDataValue
        else:
            Regs[MEM_WB_Read.WriteRegNum] = MEM_WB_Read.ALUResult


def Print_out_everything():
    global clock_cycle_num
    print(f'\n\nClock Cycle {clock_cycle_num}')
    print('--------------')
    for i, r in enumerate(Regs):
        print(f'Register {i}: {hex(r)}')
    clock_cycle_num += 1
    
    print('\nIF/ID_Write')
    print('-----------')
    print(IF_ID_Write)
    
    print('\nIF/ID_Read')
    print('----------')
    print(IF_ID_Read)
    
    print('\nID/EX_Write')
    print('-----------')
    print(ID_EX_Write)
    
    print('\nID/EX_Read')
    print('----------')
    print(ID_EX_Read)
    
    print('\nEX/MEM_Write')
    print('------------')
    print(EX_MEM_Write)
    
    print('\nEX/MEM_Read')
    print('-----------')
    print(EX_MEM_Read)
    
    print('\nMEM/WB_Write')
    print('------------')
    print(MEM_WB_Write)
    
    print('\nMEM/WB_Read')
    print('-----------')
    print(MEM_WB_Read)

def Copy_write_to_read():
    global IF_ID_Read, ID_EX_Read, EX_MEM_Read, MEM_WB_Read
    IF_ID_Read = deepcopy(IF_ID_Write)
    ID_EX_Read = deepcopy(ID_EX_Write)
    EX_MEM_Read = deepcopy(EX_MEM_Write)
    MEM_WB_Read = deepcopy(MEM_WB_Write)

# =============================================================================
# ============================== INITIALIZATIONS ==============================
# =============================================================================

# initialize main memory
MAX_MEM_ADDR = 0x400
Main_Mem = [i % 256 for i in range(MAX_MEM_ADDR)]

# initialize registers
Regs = [0]
Regs += [i for i in range(0x101, 0x120)]

# initialize pipeline registers to nops
IF_ID_Write = IF_ID_pipeline(0)
IF_ID_Read = IF_ID_pipeline(0)
ID_EX_Write = ID_EX_pipeline(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
ID_EX_Read = ID_EX_pipeline(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
EX_MEM_Write = EX_MEM_pipeline(0, 0, 0, 0, 0, 0, 0)
EX_MEM_Read = EX_MEM_pipeline(0, 0, 0, 0, 0, 0, 0)
MEM_WB_Write = MEM_WB_pipeline(0, 0, 0, 0, 0)
MEM_WB_Read = MEM_WB_pipeline(0, 0, 0, 0, 0)

# keep track of clock cycle
clock_cycle_num = 0

# =============================================================================
# =============================== MAIN PROGRAM ================================
# =============================================================================

# given instructions
InstructionCache = [0xa1020000, 0x810AFFFC, 0x00831820, 0x01263820, 0x01224820,
                    0x81180000, 0x81510010, 0x00624022, 0x00000000, 0x00000000,
                    0x00000000, 0x00000000]

# print clock cycle 0
Print_out_everything()

# loop through instruction and run through pipeline
for index in range(len(InstructionCache)):
    IF_stage()
    ID_stage()
    EX_stage()
    MEM_stage()
    WB_stage()
    Print_out_everything()
    Copy_write_to_read()
