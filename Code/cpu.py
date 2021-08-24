"""

This file, cpu.py is made for representation CPU 6502 in NES.

Hardware Description

1. Adressing Mode

(1) Implicit
    No operand needed.

    ex) Clear Carry Flag (CLC)

(2) Accumulator
    No operand needed.
    Operate with Accumulator value.

    ex) LSR A;  Logical shift right one bit

(3) Immediate
    Directly specify an 8bit constant value within the instruction

    ex) LDA $0a;    Load 10 into the accumulator

(4) Zero Page
    Zero Page means addresses $0000-$00FF. You only need to supply the low byte of the address.
    The $00 high byte is automatically added by the processor.

    ex) LDA $a0;    Load value from $00a0 to Accumulator

(5) Zero Page, X or Y
    The address is calculated by adding current value of the X or Y register to Zero Page address.
    If the sum of address and register value exceed $FF, wraps around!
    (e.g. $80 + $ff = $7f not $017f)

    ex) LDX $10, Y; Load value from $10 + the value of register Y to register X

(6) Relative
    Used by branch instruction which contain 8 signed bit relative offset (e.g. -128 to +127).
    Add value to program counter if zero flag is true.
    As the program counter is incremented itself while during instruction execution,
    the target instruction must be with -126 to 129 bytes of the offset.

(7) Absolute
    Instructions using absolute addressing contain a full 16 bit address to identify the target location.

    ex) JMP $8053;  Jump to location $8053

(8) Absolute, X or Y
    The address is calculated by sum of 16bit address and the value of X or Y register.

    ex) If X contains $92 then
        STA $2000, X;   Store accumulator value at $2092 (i.e. $2000 + $92)

(9) Indirect
    if location $0120 contains $FC and location $0121 contains $BA
    then the instruction JMP $0120 will cause the next instruction execution to occur at $BAFC.

(10) Pre - Indexed Indirect
     This mode accepts a zero-page address and adds the contents of the X-register to get an address.
     Sum the operand and the X-register to get the address to read from. Read the 2-byte address.
     Return the value found in the address.

     ex) LDA ($40, X);  Read the memory address located at $40 + X($06) => ($46).

(11) Post - Indexed Indirect
     This mode is similar to Pre-Indexed Indirect Addressing, however,
     unlike the pre-indexed mode, where the X-register is added to the operand prior to reading from memory,
     post-indexed mode adds the Y-register after reading from memory.

     ex) LDA ($46), Y;  Read the memory address located at $46.
                     ;  The address there is $15. Then, add the Y-register to it, which gives us $19.

2. CPU Memory Map

--------------------------------------- $10000
    Upper Bank of Cartridge ROM
--------------------------------------- $C000
    Lower Bank of Cartridge ROM
--------------------------------------- $8000
    Cartridge RAM (may be battery-backed)
--------------------------------------- $6000
    Expansion Modules
--------------------------------------- $5000
    Input/Output
--------------------------------------- $2000
    2kB Internal RAM, mirrored 4 times
--------------------------------------- $0000

In smaller cartridges, which only have 16kB ROM, it takes place at $C000 - $FFFF leaving $8000 - $BFFF area unused.

"""

from OpCode import OpCode


class Cpu:
    def __init__(self):
        file = open('super-mario-bros.nes', 'rb')
        print('String NES^Z : ' + file.read(4).decode('ascii'))
        print('Number of 16kB ROM banks : ' + file.read(1).hex())
        print('Number of 8kB VROM banks : ' + file.read(1).hex())
        print(file.read(1).hex())
        print(file.read(1).hex())
        print('Number of 8kB RAM banks : ' + file.read(1).hex())
        print('1 for PAL cartridges, otherwise assume NTSC : ' + file.read(1).hex())
        print(file.read(6).hex())
        print()

        # HEX
        self.__Rom = []
        for i in range(32768):
            self.__Rom.append(file.read(1).hex())

        # DEC
        self.__Ram = []
        for i in range(20480):
            self.__Ram.append(0)

        self.__Ram[8194] = -10
        self.__Ram[2012] = 100

        # 24576
        # 8192
        self.__PC = 0

        # Accumulator
        self.__A = 0

        # General purpose registers
        self.__X = 0
        self.__Y = 0

        # Stack pointer
        self.__S = []
        # Push: self.__S.append(Something)
        # Pop: self.__S.pop()

        ## Process Status ##

        # Negative
        self.N = False

        # Overflow
        self.V = False

        # BRK Command
        self.B = False

        # Decimal
        self.D = False

        # IRQ Disable
        self.D = False

        # Zero
        self.Z = False

        # Carry
        self.C = False

        ## Process Status ##

    def FetchInstruction(self):
        instruction = self.__Rom[self.__PC]

        self.__PC += 1

        return instruction

    def FetchData(self, bytes):
        data = []

        for i in range(bytes, 0, -1):
            data.append(self.__Rom[self.__PC + i - 1])

        self.__PC += bytes

        return ''.join(data)

    def Branch(self, data):
        value = int(data, 16)

        if value < 128:
            self.__PC += value
        else:
            self.__PC += (value - 256)

    def ReadData(self, address):
        dec = int(address, 16)
        returnValue = -1

        if 0 <= dec < 20480:
            returnValue = self.__Ram[dec]
        elif 32768 <= dec < 65536:
            returnValue = int(self.__Rom[dec - 32768], 16)

        if returnValue > 127:
            returnValue -= 256

        return returnValue

    def ReadDataDec(self, address):
        returnValue = -1

        if 0 <= address < 20480:
            returnValue = self.__Ram[address]
        elif 32768 <= address < 65536:
            returnValue = int(self.__Rom[address - 32768], 16)

        if returnValue > 127:
            returnValue -= 256

        return returnValue

    def Indirect(self, address):
        returnValue = 0
        tmp = 0
        second = self.FetchData(1)
        dec = int(second, 16)

        if 0 <= dec < 20480:
            if self.__Ram[dec] < 0:
                tmp = self.__Ram[dec] + 256
            else:
                tmp = self.__Ram[dec]

            returnValue += tmp * 16 *16
        elif 32768 <= dec < 65536:
            returnValue += int(self.__Rom[dec - 23768], 16) * 16 * 16

        dec = int(address, 16)

        if 0 <= dec < 20480:
            if self.__Ram[dec] < 0:
                tmp = self.__Ram[dec] + 256
            else:
                tmp = self.__Ram[dec]

            returnValue += tmp
        elif 32768 <= dec < 65536:
            returnValue += int(self.__Rom[dec - 23768], 16)

        return returnValue

    def IndirectX(self, address):
        tmp = 0
        if self.__X < 0:
            tmp = self.__X + 256
        else:
            tmp = self.__X

        data = int(address, 16) + tmp

        return self.ReadDataDec(data)

    def IndirectY(self, address):
        tmp = 0
        if self.__Y < 0:
            tmp = self.__Y + 256
        else:
            tmp = self.__Y

        data = self.ReadData(address) + tmp

        return data

    def ZeroPageX(self, data):
        tmp = 0
        if self.__X < 0:
            tmp = self.__X + 256
        else:
            tmp = self.__X

        index = int(data, 16) + tmp

        return self.__Ram[index]

    def ZeroPageY(self, data):
        tmp = 0
        if self.__Y < 0:
            tmp = self.__Y + 256
        else:
            tmp = self.__Y

        index = int(data, 16) + tmp

        return self.__Ram[index]

    def AbsoluteX(self, data):
        tmp = 0
        if self.__X < 0:
            tmp = self.__X + 256
        else:
            tmp = self.__X

        address = int(data, 16) + tmp
        returnValue = self.ReadDataDec(address)

        return returnValue

    def AbsoluteY(self, data):
        tmp = 0
        if self.__Y < 0:
            tmp = self.__Y + 256
        else:
            tmp = self.__Y

        address = int(data, 16) + tmp
        returnValue = self.ReadDataDec(address)

        return returnValue

    def rotl(self, num, bits = 8):
        bit = num & (1 << (bits-1))
        num <<= 1

        if(bit):
            num |= 1

        num &= (2**bits-1)

        return num

    def rotr(self, num, bits = 8):
        num &= (2**bits-1)
        bit = num & 1
        num >>= 1

        if(bit):
            num |= (1 << (bits-1))

        return num

    def debug(self):
        print('A: ' + str(self.__A), end=' ')
        print('X: ' + str(self.__X), end=' ')
        print('Y: ' + str(self.__Y), end=' ')
        print()

        print('Z: ' + str(self.Z), end=' ')
        print('C: ' + str(self.C), end=' ')
        print('N: ' + str(self.N), end=' ')
        print()
        print()

    def PrintMem(self):
        for i in range(20480):
            if self.__Ram[i] != 0:
                print(str(i) + ': ' + str(self.__Ram[i]))

    def run(self):
        for i in range(19500):
            instruction = self.FetchInstruction()

            if instruction in OpCode.op_adc:
                self.ADC(instruction)
            elif instruction in OpCode.op_and:
                self.AND(instruction)
            elif instruction in OpCode.op_asl:
                self.ASL(instruction)
            elif instruction in OpCode.op_bcc:
                self.BCC(instruction)
            elif instruction in OpCode.op_bcs:
                self.BCS(instruction)
            elif instruction in OpCode.op_beq:
                self.BEQ(instruction)
            elif instruction in OpCode.op_bit:
                self.BIT(instruction)
            elif instruction in OpCode.op_bmi:
                self.BMI(instruction)
            elif instruction in OpCode.op_bne:
                self.BNE(instruction)
            elif instruction in OpCode.op_bpl:
                self.BPL(instruction)
            elif instruction in OpCode.op_brk:
                self.BRK(instruction)
            elif instruction in OpCode.op_bvc:
                self.BVC(instruction)
            elif instruction in OpCode.op_bvs:
                self.BVS(instruction)
            elif instruction in OpCode.op_clc:
                self.CLC(instruction)
            elif instruction in OpCode.op_cld:
                self.CLD(instruction)
            elif instruction in OpCode.op_cli:
                self.CLI(instruction)
            elif instruction in OpCode.op_clv:
                self.CLV(instruction)
            elif instruction in OpCode.op_cmp:
                self.CMP(instruction)
            elif instruction in OpCode.op_cpx:
                self.CPX(instruction)
            elif instruction in OpCode.op_cpy:
                self.CPY(instruction)
            elif instruction in OpCode.op_dec:
                self.DEC(instruction)
            elif instruction in OpCode.op_dex:
                self.DEX(instruction)
            elif instruction in OpCode.op_dey:
                self.DEY(instruction)
            elif instruction in OpCode.op_eor:
                self.EOR(instruction)
            elif instruction in OpCode.op_inc:
                self.INC(instruction)
            elif instruction in OpCode.op_inx:
                self.INX(instruction)
            elif instruction in OpCode.op_iny:
                self.INY(instruction)
            elif instruction in OpCode.op_jmp:
                self.JMP(instruction)
            elif instruction in OpCode.op_jsr:
                self.JSR(instruction)
            elif instruction in OpCode.op_lda:
                self.LDA(instruction)
            elif instruction in OpCode.op_ldx:
                self.LDX(instruction)
            elif instruction in OpCode.op_ldy:
                self.LDY(instruction)
            elif instruction in OpCode.op_lsr:
                self.LSR(instruction)
            elif instruction in OpCode.op_nop:
                self.NOP(instruction)
            elif instruction in OpCode.op_ora:
                self.ORA(instruction)
            elif instruction in OpCode.op_pha:
                self.PHA(instruction)
            elif instruction in OpCode.op_php:
                self.PHP(instruction)
            elif instruction in OpCode.op_pla:
                self.PLA(instruction)
            elif instruction in OpCode.op_plp:
                self.PLP(instruction)
            elif instruction in OpCode.op_rol:
                self.ROL(instruction)
            elif instruction in OpCode.op_ror:
                self.ROR(instruction)
            elif instruction in OpCode.op_rti:
                self.RTI(instruction)
            elif instruction in OpCode.op_rts:
                self.RTS(instruction)
            elif instruction in OpCode.op_sbc:
                self.SBC(instruction)
            elif instruction in OpCode.op_sec:
                self.SEC(instruction)
            elif instruction in OpCode.op_sed:
                self.SED(instruction)
            elif instruction in OpCode.op_sei:
                self.SEI(instruction)
            elif instruction in OpCode.op_sta:
                self.STA(instruction)
            elif instruction in OpCode.op_stx:
                self.STX(instruction)
            elif instruction in OpCode.op_sty:
                self.STY(instruction)
            elif instruction in OpCode.op_tax:
                self.TAX(instruction)
            elif instruction in OpCode.op_tay:
                self.TAY(instruction)
            elif instruction in OpCode.op_tsx:
                self.TSX(instruction)
            elif instruction in OpCode.op_txa:
                self.TXA(instruction)
            elif instruction in OpCode.op_txs:
                self.TXS(instruction)
            elif instruction in OpCode.op_tya:
                self.TYA(instruction)
            else:
                print('error')

        self.PrintMem()
            #self.debug()

    def ADC(self, instruction):
        # Immediate
        if instruction == OpCode.op_adc[0]:
            data = self.FetchData(1)

            value = int(data, 16)
            if value > 127:
                value -= 256

            self.__A += value

            print('ADC : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_adc[1]:
            data = self.FetchData(1)
            value = self.__Ram[int(data, 16)]

            self.__A += value
            
            print('ADC : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_adc[2]:
            data = self.FetchData(1)
            value = self.ZeroPageX(data)

            self.__A += value
            
            print('ADC : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_adc[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            self.__A += value
            
            print('ADC : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_adc[4]:
            data = self.FetchData(2)
            
            value = self.AbsoluteX(data)

            self.__A += value

            print('ADC : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_adc[5]:
            data = self.FetchData(2)
            
            value = self.AbsoluteY(data)

            self.__A += value

            print('ADC : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_adc[6]:
            data = self.FetchData(1)

            self.__A += self.IndirectX(data)

            print('ADC : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_adc[7]:
            data = self.FetchData(1)

            self.__A += self.IndirectY(data)

            print('ADC : ' + instruction + ' ' + data)

        if self.__A > 255:
            self.__A = 255
            self.C = True
        else:
            self.C = False
        
        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def AND(self, instruction):
        # Immediate
        if instruction == OpCode.op_and[0]:
            data = self.FetchData(1)
            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value = int(data, 16)

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('AND : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_and[1]:
            data = self.FetchData(1)
            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value = self.__Ram[int(data, 16)]
            if value < 0:
                value += 256

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('AND : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_and[2]:
            data = self.FetchData(1)
            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value = self.ZeroPageX(data)
            if value < 0:
                value += 256

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('AND : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_and[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            if value < 0:
                value += 256

            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value
        
            print('AND : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_and[4]:
            data = self.FetchData(2)
            value = self.AbsoluteX(data)

            if value < 0:
                value += 256

            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('AND : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_and[5]:
            data = self.FetchData(2)
            value = self.AbsoluteY(data)

            if value < 0:
                value += 256

            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('AND : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_and[6]:
            data = self.FetchData(1)
            value = self.IndirectX(data)

            if value < 0:
                value += 256

            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('AND : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_and[7]:
            data = self.FetchData(1)
            value = self.IndirectY(data)

            if value < 0:
                value += 256

            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value &= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('AND : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False
        
        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def ASL(self, instruction):
        if self.__A >= 128:
            self.C = True
        else:
            self.C = False
        
        # Accumulator
        if instruction == OpCode.op_asl[0]:
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            tmp <<= 1

            if tmp > 255:
                tmp -= 256
                self.V = True

            if tmp > 127:
                tmp -= 256

            self.__A = tmp

            print('ASL : ' + instruction)

        # Zero Page
        elif instruction == OpCode.op_asl[1]:
            data = self.FetchData(1)
            tmp = self.__Ram[int(data, 16)]
            if tmp < 0:
                tmp += 256

            tmp <<= 1

            if tmp > 255:
                tmp -= 256
                self.V = True

            if tmp > 127:
                tmp -= 256

            self.__Ram[int(data, 16)] = tmp

            print('ASL : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_asl[2]:
            data = self.FetchData(1)
            x = self.__X
            if x < 0:
                x += 256

            address = int(data, 16) + x
            tmp = self.__Ram[address]
            if tmp < 0:
                tmp += 256

            tmp <<= 1

            if tmp > 255:
                tmp -= 256
                self.V = True

            if tmp > 127:
                tmp -= 256

            self.__Ram[address] = tmp

            print('ASL : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_asl[3]:
            data = self.FetchData(2)
            address = int(data, 16)
            value = self.__Ram[address]

            if value < 0:
                value += 256

            value <<= 1

            if value > 255:
                value -= 256
                self.V = True

            if value > 127:
                value -= 256

            self.__Ram[address] = value

            print('ASL : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_asl[4]:
            data = self.FetchData(2)
            tmp = 0

            if self.__X < 0:
                tmp = self.__X + 256
            else:
                tmp = self.__X

            address = int(data, 16) + tmp
            value = self.__Ram[address]

            if value < 0:
                value += 256

            value <<= 1

            if value > 255:
                value -= 256
                self.V = True

            if value > 127:
                value -= 256

            self.__Ram[address] = value

            print('ASL : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def BCC(self, instruction):
        # Relative
        if instruction == OpCode.op_bcc[0]:
            data = self.FetchData(1)
            
            if self.C == False:
                self.Branch(data)

            print('BCC : ' + instruction + ' ' + data)

    def BCS(self, instruction):
        if instruction == OpCode.op_bcs[0]:
            data = self.FetchData(1)

            if self.C == True:
                self.Branch(data)
            
            print('BCS : ' + instruction + ' ' + data)

    def BEQ(self, instruction):
        if instruction == OpCode.op_beq[0]:
            data = self.FetchData(1)

            if self.Z == True:
                self.Branch(data)
            
            print('BEQ : ' + instruction + ' ' + data)

    # TODO
    def BIT(self, instruction):
        if instruction == OpCode.op_bit[0]:
            data = self.FetchData(1)
            print('BIT : ' + instruction + ' ' + data)
        elif instruction == OpCode.op_bit[1]:
            data = self.FetchData(2)
            print('BIT : ' + instruction + ' ' + data)

    def BMI(self, instruction):
        if instruction == OpCode.op_bmi[0]:
            data = self.FetchData(1)

            if self.N == True:
                self.Branch(data)
            
            print('BMI : ' + instruction + ' ' + data)

    def BNE(self, instruction):
        if instruction == OpCode.op_bne[0]:
            data = self.FetchData(1)

            if self.Z == False:
                self.Branch(data)
            
            print('BNE : ' + instruction + ' ' + data)

    def BPL(self, instruction):
        if instruction == OpCode.op_bpl[0]:
            data = self.FetchData(1)

            if self.N == False:
                self.Branch(data)
            
            print('BPL : ' + instruction + ' ' + data)

    # TODO
    def BRK(self, instruction):
        if instruction == OpCode.op_brk[0]:
            print('BRK : ' + instruction)

    def BVC(self, instruction):
        if instruction == OpCode.op_bvc[0]:
            data = self.FetchData(1)

            if self.V == False:
                self.Branch(data)
            
            print('BVC : ' + instruction + ' ' + data)

    def BVS(self, instruction):
        if instruction == OpCode.op_bvs[0]:
            data = self.FetchData(1)

            if self.V == True:
                self.Branch(data)
            
            print('BVS : ' + instruction + ' ' + data)

    def CLC(self, instruction):
        if instruction == OpCode.op_clc[0]:

            self.C = False

            print('CLC : ' + instruction)

    def CLD(self, instruction):
        if instruction == OpCode.op_cld[0]:

            self.D = False

            print('CLD : ' + instruction)

    # TODO
    def CLI(self, instruction):
        if instruction == OpCode.op_cli[0]:
            print('CLI : ' + instruction)

    def CLV(self, instruction):
        if instruction == OpCode.op_clv[0]:

            self.V = False

            print('CLV : ' + instruction)

    def CMP(self, instruction):
        value = 0

        # Immediate
        if instruction == OpCode.op_cmp[0]:
            data = self.FetchData(1)

            value = int(data, 16)
            if value > 127:
                value -= 256

            print('CMP : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_cmp[1]:
            data = self.FetchData(1)

            value = self.__Ram[int(data, 16)]

            print('CMP : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_cmp[2]:
            data = self.FetchData(1)

            tmp = self.__X
            if tmp < 0:
                tmp += 256

            value = self.__Ram[int(data, 16) + tmp]

            print('CMP : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_cmp[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            print('CMP : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_cmp[4]:
            data = self.FetchData(2)
            value = self.AbsoluteX(data)

            print('CMP : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_cmp[5]:
            data = self.FetchData(2)
            value = self.AbsoluteY(data)

            print('CMP : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_cmp[6]:
            data = self.FetchData(1)
            value = self.IndirectX(data)

            print('CMP : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_cmp[7]:
            data = self.FetchData(1)
            value = self.IndirectY(data)

            print('CMP : ' + instruction + ' ' + data)

        if self.__A >= value:
            self.C = True
        else:
            self.C = False

        if self.__A == value:
            self.Z = True
        else:
            self.Z = False

    def CPX(self, instruction):
        value = 0

        # Immediate
        if instruction == OpCode.op_cpx[0]:
            data = self.FetchData(1)
            
            value = int(data, 16)
            if value > 127:
                value -= 256

            print('CPX : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_cpx[1]:
            data = self.FetchData(1)
            value = self.__Ram[int(data, 16)]

            print('CPX : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_cpx[2]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            print('CPX : ' + instruction + ' ' + data)

        if self.__X >= value:
            self.C = True
        else:
            self.C = False

        if self.__X == value:
            self.Z = True
        else:
            self.Z = False

    def CPY(self, instruction):
        value = 0

        # Immediate
        if instruction == OpCode.op_cpy[0]:
            data = self.FetchData(1)
            
            value = int(data, 16)
            if value > 127:
                value -= 256

            print('CPY : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_cpy[1]:
            data = self.FetchData(1)
            value = self.__Ram[int(data, 16)]

            print('CPY : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_cpy[2]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            print('CPY : ' + instruction + ' ' + data)

        if self.__Y >= value:
            self.C = True
        else:
            self.C = False

        if self.__Y == value:
            self.Z = True
        else:
            self.Z = False

    def DEC(self, instruction):
        # Zero Page
        if instruction == OpCode.op_dec[0]:
            data = self.FetchData(1)

            if self.__Ram[int(data, 16)] == -128:
                self.__Ram[int(data, 16)] = 127
            else:
                self.__Ram[int(data, 16)] -= 1

            if self.__Ram[int(data, 16)] == 0:
                self.Z = True
            else:
                self.Z = False
            
            if self.__Ram[int(data, 16)] < 0:
                self.N = True
            else:
                self.N = False
            
            print('DEC : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_dec[1]:
            data = self.FetchData(1)

            tmp = self.__X
            if tmp < 0:
                tmp += 256

            index = int(data, 16) + tmp

            if self.__Ram[index] == -128:
                self.__Ram[index] = 127
            else:
                self.__Ram[index] -= 1

            if self.__Ram[index] == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Ram[index] < 0:
                self.N = True
            else:
                self.N = False
            
            print('DEC : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_dec[2]:
            data = self.FetchData(2)

            if self.__Ram[int(data, 16)] == -128:
                self.__Ram[int(data, 16)] = 127
            else:
                self.__Ram[int(data, 16)] -= 1

            if self.__Ram[int(data, 16)] == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Ram[int(data, 16)] < 0:
                self.N = True
            else:
                self.N = False
            
            print('DEC : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_dec[3]:
            data = self.FetchData(2)
            tmp = 0

            if self.__X < 0:
                tmp = self.__X + 256
            else:
                tmp = self.__X

            index = int(data, 16) + tmp

            if self.__Ram[index] == -128:
                self.__Ram[index] = 127
            else:
                self.__Ram[index] -= 1

            if self.__Ram[index] == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Ram[index] < 0:
                self.N = True
            else:
                self.N = False
            
            print('DEC : ' + instruction + ' ' + data)

    def DEX(self, instruction):
        if instruction == OpCode.op_dex[0]:
            if self.__X == -128:
                self.__X = 127
            else:
                self.__X -= 1

            if self.__X == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__X < 0:
                self.N = True
            else:
                self.N = False
            
            print('DEX : ' + instruction)

    def DEY(self, instruction):
        if instruction == OpCode.op_dey[0]:
            if self.__Y == -128:
                self.__Y = 127
            else:
                self.__Y -= 1

            if self.__Y == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Y < 0:
                self.N = True
            else:
                self.N = False
            
            print('DEY : ' + instruction)

    def EOR(self, instruction):
        # Immediate
        if instruction == OpCode.op_eor[0]:
            data = self.FetchData(1)

            tmp = self.__A
            if tmp < 0:
                tmp += 256

            tmp ^= int(data, 16)

            if tmp > 127:
                tmp -= 256

            self.__A = tmp

            print('EOR : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_eor[1]:
            data = self.FetchData(1)

            tmp = self.__A
            if tmp < 0:
                tmp += 256

            value = self.__Ram[int(data, 16)]
            if value < 0:
                value += 256

            value ^= tmp

            if value > 127:
                value -= 256

            self.__A = value
            
            print('EOR : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_eor[2]:
            data = self.FetchData(1)

            tmp = self.__A
            if tmp < 0:
                tmp += 256

            x = self.__X
            if x < 0:
                x += 256

            value = self.__Ram[int(data, 16) + x]
            if value < 0:
                value += 256

            value ^= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('EOR : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_eor[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)
            tmp = 0

            if self.__A < 0:
                tmp = self.__A + 256
            else:
                tmp = self.__A

            if value < 0:
                value += 256
            
            value ^= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('EOR : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_eor[4]:
            data = self.FetchData(2)
            value = self.AbsoluteX(data)
            tmp = 0

            if self.__A < 0:
                tmp = self.__A + 256
            else:
                tmp = self.__A

            if value < 0:
                value += 256
            
            value ^= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('EOR : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_eor[5]:
            data = self.FetchData(2)
            value = self.AbsoluteY(data)
            tmp = 0

            if self.__A < 0:
                tmp = self.__A + 256
            else:
                tmp = self.__A

            if value < 0:
                value += 256
            
            value ^= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('EOR : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_eor[6]:
            data = self.FetchData(1)

            tmp = self.__A
            if tmp < 0:
                tmp += 256

            value = self.IndirectX(data)
            if value < 0:
                value += 256

            value ^= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('EOR : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_eor[7]:
            data = self.FetchData(1)

            tmp = self.__A
            if tmp < 0:
                tmp += 256

            value = self.IndirectY(data)
            if value < 0:
                value += 256

            value ^= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('EOR : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def INC(self, instruction):
        # Zero Page
        if instruction == OpCode.op_inc[0]:
            data = self.FetchData(1)

            if self.__Ram[int(data)] == 127:
                self.__Ram[int(data)] = -128
            else:
                self.__Ram[int(data)] += 1

            if self.__Ram[int(data)] == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Ram[int(data)] < 0:
                self.N = True
            else:
                self.N = False

            print('INC : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_inc[1]:
            data = self.FetchData(1)

            x = self.__X
            if x < 0:
                x += 256

            index = int(data, 16) + x

            if self.__Ram[index] == 127:
                self.__Ram[index] = -128
            else:
                self.__Ram[index] += 1

            if self.__Ram[index] == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Ram[index] < 0:
                self.N = True
            else:
                self.N = False
            
            print('INC : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_inc[2]:
            data = self.FetchData(2)

            if self.__Ram[int(data)] == 127:
                self.__Ram[int(data)] = -128
            else:
                self.__Ram[int(data)] += 1

            if self.__Ram[int(data)] == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Ram[int(data)] < 0:
                self.N = True
            else:
                self.N = False
                        
            print('INC : ' + instruction + ' ' + data)
        
        # Absolute, X
        elif instruction == OpCode.op_inc[3]:
            data = self.FetchData(2)
            tmp = 0

            if self.__X < 0:
                tmp = self.__X + 256
            else:
                tmp = self

            index = int(data, 16) + tmp

            if self.__Ram[index] == 127:
                self.__Ram[index] = -128
            else:
                self.__Ram[index] += 1

            if self.__Ram[index] == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Ram[index] < 0:
                self.N = True
            else:
                self.N = False
            
            print('INC : ' + instruction + ' ' + data)

    def INX(self, instruction):
        if instruction == OpCode.op_inx[0]:

            if self.__X == 127:
                self.__X = -128
            else:
                self.__X += 1

            if self.__X == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__X < 0:
                self.N = True
            else:
                self.N = False

            print('INX : ' + instruction)

    def INY(self, instruction):
        if instruction == OpCode.op_iny[0]:

            if self.__Y == 127:
                self.__Y = -128
            else:
                self.__Y += 1

            if self.__Y == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Y < 0:
                self.N = True
            else:
                self.N = False

            print('INY : ' + instruction)

    def JMP(self, instruction):
        # Absolute
        if instruction == OpCode.op_jmp[0]:
            data = self.FetchData(2)
            self.__PC = int(data, 16) - 32768

            print('JMP : ' + instruction + ' ' + data)

        # Indirect
        elif instruction == OpCode.op_jmp[1]:
            data = self.FetchData(2)
            self.__PC = self.Indirect(data)
            print('JMP : ' + instruction + ' ' + data)

    def JSR(self, instruction):
        # Absolute
        if instruction == OpCode.op_jsr[0]:
            data = self.FetchData(2)

            self.__S.append(self.__PC)
            self.__PC = int(data, 16) - 32768

            print('JSR : ' + instruction + ' ' + data)

    def LDA(self, instruction):
        # Absolute
        if instruction == OpCode.op_lda[0]:
            data = self.FetchData(1)
            value = int(data, 16)

            if value > 127:
                value -= 256

            self.__A = value

            print('LDA : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_lda[1]:
            data = self.FetchData(1)

            self.__A = self.__Ram[int(data, 16)]

            print('LDA : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_lda[2]:
            data = self.FetchData(1)

            self.__A = self.ZeroPageX(data)

            print('LDA : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_lda[3]:
            data = self.FetchData(2)

            self.__A = self.ReadData(data)

            print('LDA : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_lda[4]:
            data = self.FetchData(2)

            self.__A = self.AbsoluteX(data)

            print('LDA : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_lda[5]:
            data = self.FetchData(2)

            self.__A = self.AbsoluteY(data)

            print('LDA : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_lda[6]:
            data = self.FetchData(1)

            self.__A = self.IndirectX(data)

            print('LDA : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_lda[7]:
            data = self.FetchData(1)

            self.__A = self.IndirectY(data)

            print('LDA : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def LDX(self, instruction):
        # Immediate
        if instruction == OpCode.op_ldx[0]:
            data = self.FetchData(1)

            value = int(data, 16)
            if value > 127:
                value -= 256

            self.__X = value

            print('LDX : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_ldx[1]:
            data = self.FetchData(1)

            self.__X = self.__Ram[int(data, 16)]

            print('LDX : ' + instruction + ' ' + data)

        # Zero Page, Y
        elif instruction == OpCode.op_ldx[2]:
            data = self.FetchData(1)

            self.__X = self.ZeroPageY(data)

            print('LDX : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_ldx[3]:
            data = self.FetchData(2)

            self.__X = self.ReadData(data)

            print('LDX : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_ldx[4]:
            data = self.FetchData(2)

            self._X = self.AbsoluteY(data)

            print('LDX : ' + instruction + ' ' + data)

        if self.__X == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__X < 0:
            self.N = True
        else:
            self.N = False

    def LDY(self, instruction):
        # Immediate
        if instruction == OpCode.op_ldy[0]:
            data = self.FetchData(1)

            value = int(data, 16)
            if value > 127:
                value -= 256

            self.__Y = value

            print('LDY : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_ldy[1]:
            data = self.FetchData(1)

            self.__Y = self.__Ram[int(data, 16)]

            print('LDY : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_ldy[2]:
            data = self.FetchData(1)

            self.__Y = self.ZeroPageX(data)

            print('LDY : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_ldy[3]:
            data = self.FetchData(2)

            self.__Y = self.ReadData(data)

            print('LDY : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_ldy[4]:
            data = self.FetchData(2)

            self.__Y = self.AbsoluteX(data)

            print('LDY : ' + instruction + ' ' + data)

        if self.__Y == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__Y < 0:
            self.N = True
        else:
            self.N = False

    def LSR(self, instruction):
        # Accumulate
        if instruction == OpCode.op_lsr[0]:
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            if tmp % 2 == 0:
                self.C = False
            else:
                self.C = True

            tmp >>= 1

            if tmp > 127:
                tmp -= 256

            self.__A = tmp

            print('LSR : ' + instruction)

        # Zero Page
        elif instruction == OpCode.op_lsr[1]:
            data = self.FetchData(1)
            dec = int(data, 16)
            value = self.__Ram[dec]
            if value < 0:
                value += 256

            if value % 2 == 0:
                self.C = False
            else:
                self.C = True

            value >>= 1

            if value > 127:
                value -= 256

            self.__Ram[dec] = value

            print('LSR : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_lsr[2]:
            data = self.FetchData(1)
            value = self.ZeroPageX(data)
            if value < 0:
                value += 256

            if value % 2 == 0:
                self.C = False
            else:
                self.C = True

            value >>= 1

            if value > 127:
                value -= 256

            x = self.__X
            if x < 0:
                x += 256

            self.__Ram[int(data, 16) + x] = value

            print('LSR : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_lsr[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)
            if value < 0:
                value += 256

            if value % 2 == 0:
                self.C = False
            else:
                self.C = True

            value >>= 1

            if value > 127:
                value -= 256

            self.__Ram[int(data, 16)] = value

            print('LSR : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_lsr[4]:
            data = self.FetchData(2)
            value = self.AbsoluteX(data)
            if value < 0:
                value += 256

            if value % 2 == 0:
                self.C = False
            else:
                self.C = True

            value >>= 1

            if value > 127:
                value -= 256

            x = self.__X
            if x < 0:
                x += 256

            self.__Ram[int(data, 16) + x] = value

            print('LSR : ' + instruction + ' ' + data)

    def NOP(self, instruction):
        if instruction == OpCode.op_nop[0]:
            print('NOP : ' + instruction)

    def ORA(self, instruction):
        # Immediate
        if instruction == OpCode.op_ora[0]:
            data = self.FetchData(1)
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            tmp |= int(data, 16)

            if tmp > 127:
                tmp -= 256

            self.__A = tmp

            print('ORA : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_ora[1]:
            data = self.FetchData(1)
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            value = self.__Ram[int(data, 16)]
            if value < 0:
                value += 256

            value |= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('ORA : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_ora[2]:
            data = self.FetchData(1)
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            value = self.ZeroPageX(data)
            if value < 0:
                value += 256

            value |= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('ORA : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_ora[3]:
            data = self.FetchData(2)
            tmp = 0

            if self.__A < 0:
                tmp = self.__A + 256
            else:
                tmp = self.__A

            value = self.ReadData(data)

            if value < 0:
                value += 256

            value |= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('ORA : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_ora[4]:
            data = self.FetchData(2)
            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value = self.AbsoluteX(data)

            if value < 0:
                value += 256

            value |= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('ORA : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_ora[5]:
            data = self.FetchData(2)
            tmp = self.__A

            if tmp < 0:
                tmp += 256

            value = self.AbsoluteY(data)

            if value < 0:
                value += 256

            value |= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('ORA : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_ora[6]:
            data = self.FetchData(1)
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            value = self.IndirectX(data)
            if value < 0:
                value += 256

            value |= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('ORA : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_ora[7]:
            data = self.FetchData(1)
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            value = self.IndirectY(data)
            if value < 0:
                value += 256

            value |= tmp

            if value > 127:
                value -= 256

            self.__A = value

            print('ORA : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def PHA(self, instruction):
        if instruction == OpCode.op_pha[0]:
            self.__S.append(self.__A)

            print('PHA : ' + instruction)

    # TODO
    def PHP(self, instruction):
        if instruction == OpCode.op_php[0]:
            print('PHP : ' + instruction)

    def PLA(self, instruction):
        if instruction == OpCode.op_pla[0]:
            self.__A = self.__S.pop()

            print('PLA : ' + instruction)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    # TODO
    def PLP(self, instruction):
        if instruction == OpCode.op_plp[0]:
            print('PLP : ' + instruction)

    def ROL(self, instruction):
        # Accumulator
        if instruction == OpCode.op_rol[0]:
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            tmp = self.rotl(tmp)

            if tmp > 127:
                tmp -= 256

            self.__A = tmp

            print('ROL : ' + instruction)

        # Zero Page
        elif instruction == OpCode.op_rol[1]:
            data = self.FetchData(1)
            index = int(data, 16)

            tmp = self.__Ram[index]
            if tmp < 0:
                tmp += 256

            tmp = self.rotl(tmp)

            if tmp > 127:
                tmp -= 256

            self.__Ram[index] = tmp

            print('ROL : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_rol[2]:
            data = self.FetchData(1)
            x = self.__X
            if x < 0:
                x += 256

            index = int(data, 16) + x

            tmp = self.__Ram[index]
            if tmp < 0:
                tmp += 256

            tmp = self.rotl(tmp)

            if tmp > 127:
                tmp -= 256

            self.__Ram[index] = tmp

            print('ROL : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_rol[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            if value < 0:
                value += 256

            value = self.rotl(value)

            if value > 127:
                value -= 256
            
            self.__Ram[int(data, 16)] = value

            print('ROL : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_rol[4]:
            data = self.FetchData(2)
            tmp = self.__X

            if tmp < 0:
                tmp += 256

            address = int(data, 16) + tmp

            value = self.__Ram[address]

            if value < 0:
                value += 256

            value = self.rotl(value)

            if value > 127:
                value -= 256
            
            self.__Ram[address] = value

            print('ROL : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def ROR(self, instruction):
        # Accumulator
        if instruction == OpCode.op_ror[0]:
            tmp = self.__A
            if tmp < 0:
                tmp += 256

            tmp = self.rotr(tmp)

            if tmp > 127:
                tmp -= 256

            self.__A = tmp

            print('ROR : ' + instruction)

        # Zero Page
        elif instruction == OpCode.op_ror[1]:
            data = self.FetchData(1)
            index = int(data, 16)

            tmp = self.__Ram[index]
            if tmp < 0:
                tmp += 256

            tmp = self.rotr(tmp)

            if tmp > 127:
                tmp -= 256

            self.__Ram[index] = tmp

            print('ROR : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_ror[2]:
            data = self.FetchData(1)

            x = self.__X
            if x < 0:
                x += 256

            index = int(data, 16) + x

            tmp = self.__Ram[index]
            if tmp < 0:
                tmp += 256

            tmp = self.rotr(tmp)

            if tmp > 127:
                tmp -= 256

            self.__Ram[index] = tmp

            print('ROR : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_ror[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            if value < 0:
                value += 256

            value = self.rotr(value)

            if value > 127:
                value -= 256
            
            self.__Ram[int(data, 16)] = value
            
            print('ROR : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_ror[4]:
            data = self.FetchData(2)
            tmp = self.__X

            if tmp < 0:
                tmp += 256

            address = int(data, 16) + tmp

            value = self.__Ram[address]

            if value < 0:
                value += 256

            value = self.rotl(value)

            if value > 127:
                value -= 256
            
            self.__Ram[address] = value

            print('ROR : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    # TODO
    def RTI(self, instruction):
        if instruction == OpCode.op_rti[0]:
            print('RTI : ' + instruction)

    def RTS(self, instruction):
        if instruction == OpCode.op_rts[0]:
            self.__PC = self.__S.pop()
            
            print('RTS : ' + instruction)

    def SBC(self, instruction):
        # Immediate
        if instruction == OpCode.op_sbc[0]:
            data = self.FetchData(1)
            
            value = int(data, 16)
            if value > 127:
                value -= 256

            self.__A -= value
          
            print('SBC : ' + instruction + ' ' + data)

        # Zero Page
        elif instruction == OpCode.op_sbc[1]:
            data = self.FetchData(1)
            value = self.ReadData(data)

            self.__A -= value

            print('SBC : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_sbc[2]:
            data = self.FetchData(1)
            value = self.ZeroPageX(data)

            self.__A -= value

            print('SBC : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_sbc[3]:
            data = self.FetchData(2)
            value = self.ReadData(data)

            self.__A -= value

            print('SBC : ' + instruction + ' ' + data)
        
        # Absolute, X
        elif instruction == OpCode.op_sbc[4]:
            data = self.FetchData(2)
            value = self.AbsoluteX(data)

            self.__A -= value

            print('SBC : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_sbc[5]:
            data = self.FetchData(2)
            value = self.AbsoluteY(data)

            self.__A -= value

            print('SBC : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_sbc[6]:
            data = self.FetchData(1)
            value = self.IndirectX(data)

            self.__A -= value

            print('SBC : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_sbc[7]:
            data = self.FetchData(1)
            value = self.IndirectY(data)

            self.__A -= value

            print('SBC : ' + instruction + ' ' + data)

        if self.__A == 0:
            self.Z = True
        else:
            self.Z = False

        if self.__A > 255:
            self.C = False
            self.V = True
            self.__A = 255
        else:
            self.C = True
            self.V = False

        if self.__A < 0:
            self.N = True
        else:
            self.N = False

    def SEC(self, instruction):
        if instruction == OpCode.op_sec[0]:
            self.C = True

            print('SEC : ' + instruction)

    def SED(self, instruction):
        if instruction == OpCode.op_sed[0]:
            self.D = True

            print('SED : ' + instruction)

    # TODO
    def SEI(self, instruction):
        if instruction == OpCode.op_sei[0]:
            print('SEI : ' + instruction)

    def STA(self, instruction):
        # Zero Page
        if instruction == OpCode.op_sta[0]:
            data = self.FetchData(1)

            self.__Ram[int(data, 16)] = self.__A

            print('STA : ' + instruction + ' ' + data)

        # Zero Page, X
        elif instruction == OpCode.op_sta[1]:
            data = self.FetchData(1)
            x = self.__X
            if x < 0:
                x += 256

            self.__Ram[(int(data, 16) + x)] = self.__A

            print('STA : ' + instruction + ' ' + data)

        # Absolute
        elif instruction == OpCode.op_sta[2]:
            data = self.FetchData(2)

            self.__Ram[int(data, 16)] = self.__A

            print('STA : ' + instruction + ' ' + data)

        # Absolute, X
        elif instruction == OpCode.op_sta[3]:
            data = self.FetchData(2)
            tmp = self.__X

            if tmp < 0:
                tmp += 256

            self.__Ram[int(data, 16) + tmp] = self.__A

            print('STA : ' + instruction + ' ' + data)

        # Absolute, Y
        elif instruction == OpCode.op_sta[4]:
            data = self.FetchData(2)
            tmp = self.__Y

            if tmp < 0:
                tmp += 256

            self.__Ram[int(data, 16) + tmp] = self.__A

            print('STA : ' + instruction + ' ' + data)

        # Indirect, X
        elif instruction == OpCode.op_sta[5]:
            data = self.FetchData(1)
            x = self.__X
            if x < 0:
                x += 256

            address = int(data, 16) + x

            self.__Ram[address] = self.__A

            print('STA : ' + instruction + ' ' + data)

        # Indirect, Y
        elif instruction == OpCode.op_sta[6]:
            data = self.FetchData(1)
            y = self.__Y
            if y < 0:
                y += 256

            address = self.ReadData(data) + y

            self.__Ram[address] = self.__A

            print('STA : ' + instruction + ' ' + data)

    def STX(self, instruction):
        # Zero Page
        if instruction == OpCode.op_stx[0]:
            data = self.FetchData(1)
            self.__Ram[int(data, 16)] = self.__X

            print('STX : ' + instruction + ' ' + data)

        # Zero Page, Y
        if instruction == OpCode.op_stx[1]:
            data = self.FetchData(1)
            y = self.__Y
            if y < 0:
                y += 256

            self.__Ram[int(data, 16) + y] = self.__X

            print('STX : ' + instruction + ' ' + data)

        # Absolute
        if instruction == OpCode.op_stx[2]:
            data = self.FetchData(2)
            self.__Ram[int(data, 16)] = self.__X

            print('STX : ' + instruction + ' ' + data)

    def STY(self, instruction):
        # Zero Page
        if instruction == OpCode.op_sty[0]:
            data = self.FetchData(1)
            self.__Ram[int(data, 16)] = self.__Y

            print('STY : ' + instruction + ' ' + data)

        # Zero Page, X
        if instruction == OpCode.op_sty[1]:
            data = self.FetchData(1)
            x = self.__X
            if x < 0:
                x += 256

            self.__Ram[int(data, 16) + x] = self.__Y

            print('STY : ' + instruction + ' ' + data)

        # Absolute
        if instruction == OpCode.op_sty[2]:
            data = self.FetchData(2)
            self.__Ram[int(data, 16)] = self.__Y

            print('STY : ' + instruction + ' ' + data)

    def TAX(self, instruction):     
        if instruction == OpCode.op_tax[0]:
            self.__X = self.__A

            print('TAX : ' + instruction)

            if self.__X == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__X < 0:
                self.N = True
            else:
                self.N = False

    def TAY(self, instruction):
        if instruction == OpCode.op_tay[0]:
            self.__Y = self.__A

            print('TAY : ' + instruction)

            if self.__Y == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__Y < 0:
                self.N = True
            else:
                self.N = False

    def TSX(self, instruction):
        if instruction == OpCode.op_tsx[0]:
            self.__X = self.__S.pop()

            print('TSX : ' + instruction)

            if self.__X == 0:
                self.Z = True
            else:
                self.Z = False

            if self.__X < 0:
                self.N = True
            else:
                self.N = False

    def TXA(self, instruction):
        if instruction == OpCode.op_txa[0]:
            self.__A = self.__X

            print('TXA : ' + instruction)

            if self.__A == 0:
                self.Z = True
            else:
                self.Z = False
            
            if self.__A < 0:
                self.N = True
            else:
                self.N = False

    def TXS(self, instruction):
        if instruction == OpCode.op_txs[0]:
            self.__S.append(self.__X)

            print('TXS : ' + instruction)

    def TYA(self, instruction):
        if instruction == OpCode.op_tya[0]:
            self.__A = self.__Y

            print('TYA : ' + instruction)

            if self.__A == 0:
                self.Z = True
            else:
                self.Z = False
            
            if self.__A < 0:
                self.N = True
            else:
                self.N = False


if __name__ == '__main__':
    CPU = Cpu()
    CPU.run()
    CPU.debug()

