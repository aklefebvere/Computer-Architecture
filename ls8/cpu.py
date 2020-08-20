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
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.ADD = 0b10100000
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001

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
            self.reg[reg_a] *= self.reg[reg_b]
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
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value
    
    def run(self):
        """Run the CPU."""
        running = True
        self.reg[self.sp] = 0xf4
        
        while running:
            cmd = self.ram_read(self.pc)
            
            if cmd == self.LDI:
                reg_index = self.ram[self.pc + 1]
                num_for_reg = self.ram[self.pc + 2]

                self.reg[reg_index] = num_for_reg

                self.op_size = (cmd >> 6) + 1

            elif cmd == self.PRN:
                reg_index = self.ram[self.pc + 1]
                
                print(self.reg[reg_index])

                self.op_size = (cmd >> 6) + 1
            

            elif cmd == self.ADD:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu("ADD", reg_a, reg_b)

                self.op_size = (cmd >> 6) + 1

            elif cmd == self.MUL:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu("MUL", reg_a, reg_b)

                self.op_size = (cmd >> 6) + 1

            elif cmd == self.HLT:
                running = False

                self.op_size = (cmd >> 6) + 1

            elif cmd == self.PUSH:
                reg_index = self.ram[self.pc + 1]
                value = self.reg[reg_index]

                self.reg[self.sp] -= 1

                self.ram[self.reg[self.sp]] = value

                self.op_size = (cmd >> 6) + 1
                
            elif cmd == self.POP:
                reg_index = self.ram[self.pc + 1]
                value = self.ram[self.reg[self.sp]]

                self.reg[reg_index] = value

                self.reg[self.sp] += 1

                self.op_size = (cmd >> 6) + 1
            
            elif cmd == self.CALL:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = (self.pc + 2)

                reg_index = self.ram[self.pc + 1]
                self.pc = self.reg[reg_index]

                self.op_size = 0

            elif cmd == self.RET:
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1

                self.op_size = 0

            self.pc += self.op_size
        



