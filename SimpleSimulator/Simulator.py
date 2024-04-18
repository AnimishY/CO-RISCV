import sys

def twoscomp(val: int, length: int = 32):
    max_val = 2 ** length
    final = max_val - val
    return format(final, f'0{length}b')

mem = {
65536 : 0 ,65540 : 0 ,65544 : 0 , 65548 : 0 , 65552 : 0 , 65556 : 0 , 65560 : 0 , 65564 : 0 , 65568 : 0 , 65572 : 0 , 65576 : 0 , 65580 : 0 , 65584 : 0 , 65588 : 0 , 65592 : 0 , 65596 : 0 , 65600 : 0 , 65604 : 0 , 65608 : 0 , 65612 : 0 , 65616 : 0 , 65620 : 0 , 65624 : 0 , 65628 : 0 , 65632 : 0 , 65636 : 0 , 65640 : 0 ,65644 : 0 , 65648 : 0 , 65652 : 0 , 65656 : 0 , 65660 : 0 ,
256 : 0 , 260 : 0 , 264 : 0 , 268 : 0 , 272 : 0 , 276 : 0 , 280 : 0 , 284 : 0 , 288 : 0 , 292 : 0 , 296 : 0 , 300 : 0 , 304 : 0 , 308 : 0 , 312 : 0 , 316 : 0 , 320 : 0 , 324 : 0 , 328 : 0 , 332 : 0 , 336 : 0 , 340 : 0 , 344 : 0 , 348 : 0 , 352 : 0 , 356 : 0 , 360 : 0 , 364 : 0 , 368 : 0 , 372 : 0 , 376 : 0 , 380 : 0
}

registers = {'00000': 0, '00001': 0, '00010': 256, '00011': 0, '00100': 0, '00101': 0, '00110': 0, '00111': 0, '01000': 0, '01001': 0, '01010': 0, '01011': 0, '01100': 0, '01101': 0, '01110': 0, '01111': 0, '10000': 0, '10001': 0, '10010': 0, '10011': 0, '10100': 0, '10101': 0, '10110': 0, '10111': 0, '11000': 0, '11001': 0, '11010': 0, '11011': 0, '11100': 0, '11101': 0, '11110': 0, '11111': 0}

R_ops = {
    "add": ("0110011","000","0000000"),
    "sub": ("0110011","000","0100000"),
    "sll": ("0110011","001","0000000"),
    "slt": ("0110011","010","0000000"),
    "sltu": ("0110011","011","0000000"),
    "xor": ("0110011","100","0000000"),
    "srl": ("0110011","101","0000000"),
    "or": ("0110011","110","0000000"),
    "and": ("0110011","111","0000000")
}

I_ops = {
    "lw": ("0000011", "010"),
    "addi": ("0010011", "000"),
    "sltiu": ("0010011", "011"),
    "jalr": ("1100111", "000"),
}

S_ops = {
    "sw" : ("0100011", "010"),
}

J_ops = {
    "jal" : ("1101111")
}

U_ops = {
    "lui": ("0110111"),
    "auipc": ("0010111"),
}

B_ops = {
  "beq": ("1100011", "000"), 
  "bne": ("1100011", "001"),  
  "blt": ("1100011", "100"),  
  "bge": ("1100011", "101"),  
  "bltu": ("1100011", "110"), 
  "bgeu": ("1100011", "111"), 
}

class Instr:
    def __init__(self, ins: str, pc: int) -> None:
        self.instr = ins
        self.opcode = ins[-7:]
        self.pc = pc

    @staticmethod
    def parse(i: str, y: list):
        x = [i[y[j]:y[j + 1]] for j in range(len(y) - 1)]
        j = [i[:y[0]]]
        j.extend(x)
        return j

    @staticmethod
    def twoscomp(val: int, length: int = 32):
        max_val = 1 << length  # Calculate once
        final = max_val - val
        return format(final, f'0{length}b')

class I_type(Instr):
    def __init__(self, ins: str, pc: int) -> None:
        super().__init__(ins, pc)
        self.instr = self.parse(self.instr, [12, 17, 20, 25, 32])
        self.imm = self.instr[0]  # signed or unsigned check
        self.rs1 = self.instr[1]
        self.rd = self.instr[3]
        self.comp = (self.opcode, self.instr[2],)

    def execute(self):
        sextimm = int(self.imm, 2) if self.imm[0] == '0' else -int(self.twoscomp(int(self.imm, 2), 12), 2)
        if self.comp == I_ops['lw']:
            registers[self.rd] = mem[sextimm + registers[self.rs1]]
            self.pc += 4

        elif self.comp == I_ops['addi']:
            registers[self.rd] = sextimm + registers[self.rs1]
            self.pc += 4

        elif self.comp == I_ops['sltiu']:
            registers[self.rd] = 1 if sextimm > registers[self.rs1] else 0
            self.pc += 4

        elif self.comp == I_ops['jalr']:
            registers[self.rd] = self.pc + 4
            self.pc = (registers[self.rs1] + sextimm) & ~1
            if self.pc % 2 != 0:
                self.pc -= 1
            if self.pc < 0:
                self.pc = 2 ** 32 + self.pc

class R_type(Instr):
    def __init__(self,ins:str,pc:int) -> None:
        super().__init__(ins,pc)
        self.instr = self.parse(self.instr,[7,12,17,20,25,32])
        self.rs2 = self.instr[1]
        self.rs1 = self.instr[2]
        self.rd = self.instr[4]
        self.comp = (self.opcode,self.instr[3],self.instr[0])
    def execute(self):
        if self.comp == R_ops['add']:
            registers[self.rd] = registers[self.rs1] + registers[self.rs2]

        elif self.comp == R_ops['sub']:
            registers[self.rd] = registers[self.rs1] - registers[self.rs2]

        elif self.comp == R_ops['slt']:
            registers[self.rd] = 1 if registers[self.rs1] < registers[self.rs2] else 0

        elif self.comp == R_ops['sltu']:
            unsignedrs1 = 2**32 + registers[self.rs1] if registers[self.rs1] <0 else registers[self.rs1]
            unsignedrs2 = 2**32 + registers[self.rs2] if registers[self.rs2] <0 else registers[self.rs2]
            registers[self.rd] = 1 if unsignedrs1 < unsignedrs2 else 0

        elif self.comp == R_ops['xor']:
            registers[self.rd] = registers[self.rs1] ^ registers[self.rs2]

        elif self.comp == R_ops['sll']:
            registers[self.rs1] = registers[self.rs1] << int('{:032b}'.format(registers[self.rs2])[-5:],2)
            registers[self.rd] = registers[self.rs1]

        elif self.comp == R_ops['srl']:
            registers[self.rs1] = registers[self.rs1] >> int('{:032b}'.format(registers[self.rs2])[-5:],2) 
            registers[self.rd] = registers[self.rs1]

        elif self.comp == R_ops['or']:
            registers[self.rd] = registers[self.rs1] | registers[self.rs2]

        elif self.comp == R_ops['and']:
            registers[self.rd] = registers[self.rs1] & registers[self.rs2]
        self.pc += 4


class S_type(Instr):
    def __init__(self,ins:str,pc:int) -> None:
        super().__init__(ins,pc)
        self.instr = self.parse(self.instr, [7,12,17,20,25,32])
        self.imm = self.instr[0]+self.instr[4]
        self.rs2 = self.instr[1]
        self.rs1 = self.instr[2]
    def execute(self):
        sextimm = int(self.imm,2) if self.imm[0]=='0' else -int(self.twoscomp(int(self.imm,2),12),2) 
        mem[registers[self.rs1]+sextimm] = registers[self.rs2]
        self.pc += 4

class J_type(Instr):
    def __init__(self,ins:str,pc:int) -> None:
        super().__init__(ins,pc)
        self.instr=self.parse(self.instr,[20,25,32])
        self.imm = self.instr[0]
        self.rd=self.instr[1]
    def execute(self):
        registers[self.rd]=self.pc+4
        self.imm = self.imm[10:0:-1] + self.imm[11] + self.imm[19:11:-1] + self.imm[0]
        self.imm=self.imm[::-1] + '0'
        if self.imm[0] == '0':
            self.pc=self.pc+int(self.imm,2)
        else:
            self.pc=self.pc-int(self.twoscomp(int(self.imm,2),20),2)

class U_type(Instr):
    def __init__(self,ins:str,pc:int) -> None:
        super().__init__(ins,pc)
        self.instr = self.parse(self.instr, [20,25,32])
        self.imm = self.instr[0]
        self.rd = self.instr[1]
        self.op = self.instr[2]
        imm = self.imm + 12*'0'
        self.sextimm = int(imm,2) if imm[0]=='0' else -int(self.twoscomp(int(self.imm,2),32),2)
    def execute(self):
        if self.op == '0110111':
            registers[self.rd] = self.sextimm
        else:
            registers[self.rd] = self.pc + self.sextimm
        self.pc += 4

class B_type(Instr):
    def __init__(self,ins:str,pc:int) -> None:
        super().__init__(ins,pc)
        self.instr = self.parse(self.instr, [7,12,17,20,25,32])
        self.funct3 = self.instr[3]
        self.rs1 = self.instr[2]
        self.rs2 = self.instr[1]
        self.imm = self.instr[0]+self.instr[4]
        self.imm = self.imm[0]+self.imm[-1]+self.imm[1:11]
        self.imm += "0"
        self.sextimm = int(self.imm,2) if self.imm[0]=='0' else -int(self.twoscomp(int(self.imm,2),13),2) 

    def execute(self):
        unsignedrs1 = registers[self.rs1] & 0xFFFFFFFF
        unsignedrs2 = registers[self.rs2] & 0xFFFFFFFF

        if self.funct3 == '000' and unsignedrs1 == unsignedrs2:
            self.pc += self.sextimm
        elif self.funct3 == '001' and unsignedrs1 != unsignedrs2:
            self.pc += self.sextimm
        elif self.funct3 == '100' and unsignedrs1 < unsignedrs2:
            self.pc += self.sextimm
        elif self.funct3 == '101' and unsignedrs1 >= unsignedrs2:
            self.pc += self.sextimm
        elif self.funct3 == '110' and unsignedrs1 < unsignedrs2:
            self.pc += self.sextimm
        elif self.funct3 == '111' and unsignedrs1 > unsignedrs2:
            self.pc += self.sextimm
        else:
            self.pc += 4

with open(sys.argv[1], 'r') as f:
    inst = [line.strip() for line in f.readlines()]

with open(sys.argv[2], 'w') as f:
    pass 

class simulator:
    def __init__(self,instruc:list,pc:int):
        self.inst_list = instruc
        self.pc = pc
    def print_state(self, outpf):
        prefix = '0b'
        w = ''
        w+= prefix+format(self.pc,'032b')+' '
        for reg_v in list(registers.values()):
            if reg_v >= 0:
                w+=prefix+format(reg_v,'032b') + ' '
            else:
                reg_v = 2**32 + reg_v
                w+=prefix+format(reg_v,'032b') + ' '
        w += '\n'
        with open(outpf,'a') as f:
            f.write(w)
        return w
    def print_mem(self, outpf):
        prefixB, prefixH,w = '0b', '0x', ''
        for i in range(65536, 65661,4):
            mem_k = i; mem_v = mem[mem_k]
            w += prefixH+format(mem_k,'08x')+':'
            if mem_v>=0: 
                w += prefixB+format(mem_v,'032b') + '\n'

            else: 
                w += prefixB+format(mem_v+2**32,'032b') + '\n'
        with open(outpf,'a') as f:
            f.write(w)
        return w
        
    def execute(self, outpf):
        while self.inst_list[self.pc//4] != '00000000000000000000000001100011':
            pointer = self.pc//4
            opcode = self.inst_list[pointer][-7:] 
            ex = None
            if opcode == list(R_ops.values())[1][0]:
                ex = R_type(self.inst_list[pointer], self.pc)
            elif opcode == list(B_ops.values())[1][0]:
                ex = B_type(self.inst_list[pointer], self.pc)
            elif opcode in [i for i in U_ops.values()]:
                ex = U_type(self.inst_list[pointer], self.pc)
            elif opcode in [i for i in J_ops.values()]:
                ex = J_type(self.inst_list[pointer],self.pc) 
            elif opcode in [i[0] for i in I_ops.values()]:
                ex = I_type(self.inst_list[pointer],self.pc)
            elif opcode in [i[0] for i in S_ops.values()]:
                ex = S_type(self.inst_list[pointer], self.pc)
            ex.execute()
            registers['00000'] = 0
            self.pc = ex.pc
            if self.pc < 0:
                self.pc = 2**32 + self.pc
                self.print_state(outpf)
                break
            self.print_state(outpf)
        self.print_state(outpf)
        self.print_mem(outpf)

sim = simulator(inst,0)
sim.execute(sys.argv[2])
