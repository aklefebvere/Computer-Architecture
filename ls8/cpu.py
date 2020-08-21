"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram  = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.op_size = None
        self.sp = 7
        self.flags = [0,0,0]
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.ADD = 0b10100000
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.AND = 0b10101000
        self.OR = 0b10101010
        self.XOR = 0b10101011
        self.NOT = 0b01101001
        self.SHL = 0b10101100
        self.SHR = 0b10101101
        self.MOD = 0b10100100

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        with open(filename) as f:
            for line in f:
                line = line.split("#") # remove the #'s and isolate the binary value we need
                number = line[0].strip() # take out the \n's
                if number != '':
                    binary = int(number, 2) # convert to int with the base of 2 since we are passing in a b value

                    self.ram[address] = binary

                    address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_a]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flags = [1,0,0]
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = [0,1,0]
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flags = [0,0,1]
        elif op == "AND":
            self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b] == 0:
                return 0
            else:
                remainder = self.reg[reg_a] % self.reg[reg_b]
                self.reg[reg_a] = remainder

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        # return the value at an address
        return self.ram[address]

    def ram_write(self, address, value):
        # write a value into an address
        self.ram[address] = value
    
    def run(self):
        """Run the CPU."""
        # running variable to keep while loop running
        running = True
        # Define SP ram index
        self.reg[self.sp] = 0xf4

        # while loop util HALT
        while running:
            # current command
            cmd = self.ram_read(self.pc)
            # first value for cmd (if any)
            reg_a = self.ram[self.pc + 1]
            # second value for cmd (if any)
            reg_b = self.ram[self.pc + 2]
            # default op size for all commands unless overwritten
            self.op_size = (cmd >> 6) + 1
            
            # set a value to a certain reg index in the register
            if cmd == self.LDI:
                self.reg[reg_a] = reg_b
            
            # print out a value from a certain reg index
            elif cmd == self.PRN:
                print(self.reg[reg_a])

            # add two values together, storing the result in reg_a
            elif cmd == self.ADD:
                self.alu("ADD", reg_a, reg_b)

            # multiply two values together, storing the result in reg_a
            elif cmd == self.MUL:
                self.alu("MUL", reg_a, reg_b)

            # set running to False so the while loop will exit and stop the cpu
            elif cmd == self.HLT:
                running = False
            
            # push a value onto the stack stored in the ram
            elif cmd == self.PUSH:
                value = self.reg[reg_a]

                self.reg[self.sp] -= 1

                self.ram[self.reg[self.sp]] = value
            
            # pop off a value off the stack stored in the ram
            elif cmd == self.POP:
                value = self.ram[self.reg[self.sp]]

                self.reg[reg_a] = value

                self.reg[self.sp] += 1

            # Save the location of the next command and jump to the given index in the reg
            elif cmd == self.CALL:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = (self.pc + 2)

                self.pc = self.reg[reg_a]
                # op size is zero because we moved to a certain index
                self.op_size = 0

            # return to the previously saved command
            elif cmd == self.RET:
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
                # op size is zero because we moved to a certain index
                self.op_size = 0

            # Sets the flags values
            # [1,0,0] = value at reg_a < value at reg_b
            # [0,1,0] = value at reg_a > value at reg_b
            # [0,0,1] = value at reg_a == value at reg_b
            elif cmd == self.CMP:
                self.alu("CMP", reg_a, reg_b)
            
            # jump to the given index
            elif cmd == self.JMP:
                self.pc = self.reg[reg_a]
                # sinced we jumped to a different index, set op size to 0
                self.op_size = 0
            # check if the equal flag is set to 1 (true)
            # if it is, go to the given index stored in the reg
            elif cmd == self.JEQ:
                if self.flags[2] == 1:
                    self.pc = self.reg[reg_a]
                    self.op_size = 0
            # check if the equal flag is set to 0 (false)
            # if it is, go to the given index stored in the reg    
            elif cmd == self.JNE:
                if self.flags[2] == 0:
                    self.pc = self.reg[reg_a]
                    self.op_size = 0

            # Perform a bitwise and on reg_a and reg_b storing the value in reg_a
            elif cmd == self.AND:
                self.alu("AND", reg_a, reg_b)

            # Perform a bitwise or on reg_a and reg_b storing the value in reg_a
            elif cmd == self.OR:
                self.alu("OR", reg_a, reg_b)

            # Perform a bitwise XOR on reg_a and reg_b storing the value in reg_a
            elif cmd == self.XOR:
                self.alu("XOR", reg_a, reg_b)

            # Perform a bitwise not on reg_a
            elif cmd == self.NOT:
                self.alu("NOT", reg_a, reg_b)

            # Perform a bitwise left shift on reg_a and reg_b storing the value in reg_a
            elif cmd == self.SHL:
                self.alu("SHL", reg_a, reg_b)

            # Perform a bitwise right shift on reg_a and reg_b storing the value in reg_a
            elif cmd == self.SHR:
                self.alu("SHR", reg_a, reg_b)

            # Perform a modulo on reg_a and reg_b storing the remainder in reg_a
            # if the value at reg_b is 0, halt the cpu
            elif cmd == self.MOD:
                check = self.alu("MOD", reg_a, reg_b)
                if check == 0:
                    print('Error: divide by zero error, halting')
                    running = False
            
            self.pc += self.op_size
        



