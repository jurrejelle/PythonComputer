import subprocess,sys
subprocess.call('',shell=True)

# Set up registers
R1 = 0
R2 = 1
R3 = 2
R4 = 3
ACC = 4
IP = 5
SP = 6
FP = 7
REGS = ['R1','R2','R3','R4','ACC','IP', 'SP', 'FP']

#Moving stuff around
MOV_LIT_REG     = 0x10 # Move constant into register
MOV_REG_REG     = 0x11 # Move register into register
MOV_LIT_MEM     = 0x12 # Moves a literal value into memory
MOV_REG_PTR_REG = 0x13 # Gets value from a pointer in a register, and moves into register
MOV_LIT_OFF_REG = 0x14 # Move the value from [address + offset_in_register] into a register

#Stack functionality
PUSH_LIT        = 0x20 # Push a literal value to the stack
PUSH_REG        = 0x21 # Push a value from a register to the stack
POP             = 0x22 # Pop a value from the stack
CALL_LIT        = 0x23 # Make a call to a function whose pointer is a literal
CALL_REG        = 0x24 # Make a call to a function whose pointer comes from a register
RET             = 0x25 # Return back from a call instruction
HALT            = 0x26 # Halts the program

#Arithmathic operations
ADD_REG_REG     = 0x30 # Add values from registers together into ACC
ADD_LIT_REG     = 0x31 # Add a literal value to a register into ACC
SUB_LIT_REG     = 0x32 # Subtract a literal value from a register into ACC
SUB_REG_LIT     = 0x33 # Subtract a register from a literal value into ACC
SUB_REG_REG     = 0x34 # Subtract a register from a register into ACC
MUL_LIT_REG     = 0x35 # Multiply a literal value by a register into ACC
MUL_REG_REG     = 0x36 # Multiply a register by a register into ACC
INC_REG         = 0x37 # Increment a register in place
DEC_REG         = 0x38 # Decrement a register in place

#Logical operations
LSF_REG_LIT     = 0x40 # Left-shift a value in a regiser by a literal amount of bits
LSF_REG_REG     = 0x41 # Left-shift a value in a regiser by an amount of bits from a register
RSF_REG_LIT     = 0x42 # Right-shift a value in a regiser by a literal amount of bits
RSF_REG_REG     = 0x43 # Right-shift a value in a regiser by an amount of bits from a register
AND_REG_LIT     = 0x44 # Perform a bitwise AND with a register and a literal
AND_REG_REG     = 0x45 # Perform a bitwise AND with a register and a register
OR_REG_LIT      = 0x46 # Perform a bitwise OR with a register and a literal
OR_REG_REG      = 0x47 # Perform a bitwise OR with a register and a register
XOR_REG_LIT     = 0x48 # Perform a bitwise XOR with a register and a literal
XOR_REG_REG     = 0x49 # Perform a bitwise XOR with a register and a register
NOT             = 0x4a # Perform a bitwise NOT on a register

#Conditional logic
JNE_LIT         = 0x50 # Jump to address if literal value is not equal to the ACC
JNE_REG         = 0x51 # Jump to address if value from register is not equal to the ACC
JEQ_LIT         = 0x52 # Jump to address if literal value is equal to the ACC
JEQ_REG         = 0x53 # Jump to address if value from register is equal to the ACC
JLT_LIT         = 0x54 # Jump to address if literal value is less than the ACC
JLT_REG         = 0x55 # Jump to address if value from register is less than the ACC
JGT_LIT         = 0x56 # Jump to address if literal value is greater than the ACC
JGT_REG         = 0x57 # Jump to address if value from register is greater than the ACC
JLE_LIT         = 0x58 # Jump to address if literal value is less than or equal to the ACC
JLE_REG         = 0x59 # Jump to address if value from register is less than or equal to the ACC
JGE_LIT         = 0x5a # Jump to address if literal value is greater than or equal to the ACC
JGE_REG         = 0x5b # Jump to address if value from register is greater than or equal to the ACC


#Debug stuff
PRINT_REGISTERS = 0xff # Print values of all registers

# Quick shortcut for printing
def p(inp):
    print(hex(inp))

# Define a custom exception for in the memorymapper class
class AddressNotFoundException(Exception):
    pass

# Define the memorymapper class
class MemoryMapper:
    def __init__(self):
        self.regions = [];

    # The function to add a memorymap
    def map(self,device, start, end, remap = False):
        region = [device, start, end, remap]
        self.regions.insert(0,region)

    # a quick shortcut for finding which region an address is in
    def findregion(self, address):
        found = []
        for x in self.regions:
            if(address >= x[1] and address <= x[2]):
                found = x
                break
        if(not(found)):
            raise AddressNotFoundException
        return found

    # Editing the function for getting via [] for the class
    def __getitem__(self, address):
        region = self.findregion(address)
        if(region[3]):
            # Remap the address by subtracting the base of the region
            address = address - region[1]
        return region[0][address]

    # Editing the function for setting via [] for the class
    def __setitem__(self, address, value):
        region = self.findregion(address)
        if(region[3]):
            # Remap the address by subtracting the base of 
            address = address - region[1]
        region[0][address] = value

# Creating a quick screen class to play around with
class Screen:
    def __init__(self):
        pass
    #Function for printing a character to the screen properly
    def print(self,val):
        sys.stdout.write(chr(val))
        sys.stdout.flush()
    # Function to move the cursor to an x,y coordinate
    def moveTo(self,x,y):
        sys.stdout.write('\x1b['+str(x)+';'+str(y)+'H')

    # Function to set the text to bold
    def setBold(self):
        sys.stdout.write('\x1b[1m')

    # Function to set text color to red
    def setRed(self):
        sys.stdout.write('\x1b[31m')

    #Function to set text formatting back to normal
    def setRegular(self):
        sys.stdout.write('\x1b[0m')

    #Function to clear the screen
    def clearScreen(self):
        #The ANSI clear screen shortcut didn't work, so this has to do for now
        for x in range(0, 100):
            for y in range(0, 100):
                self.moveTo(x,y)
                self.print(0x20)
                
    def __getitem__(self, address):
        return 0

    # Writing to the screen is like writing to an array
    # The value you write to it is composed for 4 bytes, namely:
    # xx000000 - The character
    # 00xx0000 - The x position
    # 0000xx00 - The y position
    # 000000xx - The command 
    def __setitem__(self, address, value):
        character = (value & 0xff000000) >> 24
        xpos      = (value & 0x00ff0000) >> 16
        ypos      = (value & 0x0000ff00) >> 8
        command   = (value & 0x000000ff)
        
        self.moveTo(ypos, xpos*2+1)
        if(command==0x01):
            self.clearScreen()
        if(command==0x02):
            self.setBold()
        if(command==0x03):
            self.setRegular();
        if(command==0x04):
            self.setRed();
        if(command==0xff):
            self.clearScreen();
        sys.stdout.write(chr(character))
        sys.stdout.flush()

# The main class for the computer
# This is where most of the magic happens
class computer:
    def __init__(self, memoryMap):
        # Create a memory region for the registers
        # a 32 bit field (4 bytes) for every register
        self.registers = bytearray(len(REGS) * 4);
        # Assign the memoryMap to memory
        self.memory = memoryMap

        self.debug = False

        self.halt = False
        
        self.setregister(SP, 512-4)
        self.setregister(FP, 512-4)
        self.stackFrameSize = 0;
    # Function for putting stuff in the memory
    def upload_at_location(self, location, buffer):
        for x in range(0, len(buffer)):
            self.memory[location+x] = buffer[x]

    # Quick way to debug what's going on
    def printallregisters(self):
        for x in range(0, len(REGS)*4, 4):
            print(REGS[int(x/4)] + ' 0x{:0>2x}{:0>2x}{:0>2x}{:0>2x}'.format(self.registers[x],self.registers[x+1],self.registers[x+2],self.registers[x+3]))
        print('\n')

    # Function for getting the full 32 bit value from a register
    def getregister(self, reg):
        value = self.registers[reg*4+3]+self.registers[reg*4+2]*256+ self.registers[reg*4+1]*256*256 + self.registers[reg*4]*256*256*256
        return value;

    # Function for writing a 32 bit value to a register
    def setregister(self, reg, value):
        value = '{:0>8x}'.format(value)
        values = [value[x:x+2] for x in range(0, len(value), 2)]
        self.registers[reg*4] = int(values[0],16)
        self.registers[reg*4+1] = int(values[1],16)
        self.registers[reg*4+2] = int(values[2],16)
        self.registers[reg*4+3] = int(values[3],16)

    # Function for fetching a byte from memory at the IP
    def fetch(self):
        value = self.memory[self.getregister(IP)]
        self.setregister(IP, self.getregister(IP)+1)
        return value

    # Function for fetching two bytes from memory at the IP
    def fetch16(self):
        value = self.memory[self.getregister(IP)+1]+self.memory[self.getregister(IP)]*256
        self.setregister(IP, self.getregister(IP)+2)
        return value

    # Function for fetching a 4 byte value from memory at the IP
    def fetch32(self):
        reg = self.getregister(IP);
        value = self.memory[reg+3] + self.memory[reg+2]*256 + self.memory[reg+1]*256*256 + self.memory[reg]*256*256*256
        self.setregister(IP, reg+4)
        return value
    
    # Function to get a 4 byte value from memory at a custom location
    def fetch32at(self, location):
        value = self.memory[location+3] + self.memory[location+2]*256 + self.memory[location+1]*256*256 + self.memory[location]*256*256*256
        return value
        
    # Function to write to memory
    def write32(self, location, value):
        value = '{:0>8x}'.format(value)
        values = [value[x:x+2] for x in range(0, len(value), 2)]
        self.memory[location] = int(values[0],16)
        self.memory[location+1] = int(values[1],16)
        self.memory[location+2] = int(values[2],16)
        self.memory[location+3] = int(values[3],16)
    # Push a 32 bit value to the stack
    def push(self, value):
        spAddress = self.getregister(SP);
        self.write32(spAddress, value);
        self.setregister(SP,spAddress-4);
        self.stackFrameSize += 4;

    # Pop a 32 bit value from the stack
    def pop(self):
        nextSpAddress = self.getregister(SP) + 4;
        self.setregister(SP, nextSpAddress);
        self.stackFrameSize -= 4;
        return self.fetch32at(nextSpAddress);

    # Push the current state of the CPU to the stack
    def pushState(self):
        
        self.push(self.getregister(R1))
        self.push(self.getregister(R2))
        self.push(self.getregister(R3))
        self.push(self.getregister(R4))
        self.push(self.getregister(IP))
        self.push(self.stackFrameSize + 4)
        
        self.setregister(FP,self.getregister(SP))
        self.stackFrameSize = 0;

    # Get the current state back from the stack into the CPU
    def popState(self):
        framePointer = self.getregister(FP)
        self.setregister(SP, framePointer)
        self.stackFrameSize = self.pop()
        tempStackFrame = self.stackFrameSize;
        self.setregister(IP,self.pop())
        self.setregister(R4,self.pop())
        self.setregister(R3,self.pop())
        self.setregister(R2,self.pop())
        self.setregister(R1,self.pop())
        numberOfArgs = self.pop()
        for i in range(0, numberOfArgs):
            self.pop()
            
        self.setregister(FP, framePointer + tempStackFrame)
        
    # Execute the instruction passed to it
    def execute(self, instruction):
        if(instruction == MOV_LIT_REG):
            value = self.fetch32()
            register = self.fetch()
            self.setregister(register, value)
        if(instruction == MOV_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            self.setregister(reg2, self.getregister(reg1))
        if(instruction == MOV_LIT_MEM):
            value = self.fetch32()
            address = self.fetch32()
            self.memory[address] = value
        if(instruction == MOV_REG_PTR_REG):
            register_from = self.fetch()
            register_to = self.fetch()
            pointer = self.getregister(register_from)
            value = self.fetch32at(pointer)
            self.setregister(register_to, value)
            
        if(instruction == PUSH_LIT):
            value = self.fetch32();
            self.push(value);
        if(instruction == PUSH_REG):
            register = self.fetch();
            value = self.getregister(register);
            self.push(value);
        if(instruction == POP):
            register = self.fetch();
            value = self.pop();
            self.setregister(register, value);
        if(instruction == CALL_LIT):
            jumpAddress = self.fetch32()
            self.pushState()
            self.setregister(IP, jumpAddress);
        if(instruction == CALL_REG):
            jumpAddress = self.getregister(self.fetch())
            self.pushState()
            self.setregister(IP, jumpAddress);
        if(instruction == RET):
            self.popState();

            
        if(instruction == ADD_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            value = self.getregister(reg1) + self.getregister(reg2)
            self.setregister(ACC, value)
        if(instruction == ADD_LIT_REG):
            literal = self.fetch32()
            reg = self.fetch()
            regvalue = self.getregister(reg)
            value = literal+regvalue
            self.setregister(ACC, value)
        if(instruction == SUB_LIT_REG):
            literal = self.fetch32()
            reg = self.fetch()
            regvalue = self.getregister(reg)
            value = regvalue-literal
            self.setregister(ACC, value)
        if(instruction == SUB_REG_LIT):
            reg = self.fetch()
            literal = self.fetch32()
            regvalue = self.getregister(reg)
            value = literal-regvalue
            self.setregister(ACC, value)
        if(instruction == SUB_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            value = self.getregister(reg1) - self.getregister(reg2)
            self.setregister(ACC, value)
        if(instruction == MUL_LIT_REG):
            literal = self.fetch32()
            reg1 = self.fetch()
            value = self.getregister(reg1) * literal
            self.setregister(ACC, value)
        if(instruction == MUL_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            value = self.getregister(reg1) * self.getregister(reg2)
            self.setregister(ACC, value)
        if(instruction == INC_REG):
            reg = self.fetch() 
            self.setregister(reg, self.getregister(reg)+1)
        if(instruction == DEC_REG):
            reg = self.fetch() 
            self.setregister(reg, self.getregister(reg)-1)

        if(instruction == LSF_REG_LIT):
            reg = self.fetch()
            lit = self.fetch()
            regvalue = self.getregister(reg)
            value = regvalue << lit
            self.setregister(reg, value)
        if(instruction == LSF_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            regvalue1 = self.getregister(reg)
            regvalue2 = self.getregister(reg)
            value = regvalue1 << regvalue2
            self.setregister(reg1, value)
        if(instruction == RSF_REG_LIT):
            reg = self.fetch()
            lit = self.fetch()
            regvalue = self.getregister(reg)
            value = regvalue >> lit
            self.setregister(reg, value)
        if(instruction == RSF_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            regvalue1 = self.getregister(reg)
            regvalue2 = self.getregister(reg)
            value = regvalue1 >> regvalue2
            self.setregister(reg1, value)
        if(instruction == AND_REG_LIT):
            reg = self.fetch()
            lit = self.fetch32()
            regvalue = self.getregister(reg)
            value = regvalue & lit
            self.setregister(ACC, value)
        if(instruction == AND_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            regvalue1 = self.getregister(reg)
            regvalue2 = self.getregister(reg)
            value = regvalue1 & regvalue2
            self.setregister(ACC, value)
        if(instruction == OR_REG_LIT):
            reg = self.fetch()
            lit = self.fetch32()
            regvalue = self.getregister(reg)
            value = regvalue | lit
            self.setregister(ACC, value)
        if(instruction == OR_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            regvalue1 = self.getregister(reg)
            regvalue2 = self.getregister(reg)
            value = regvalue1 | regvalue2
            self.setregister(ACC, value)
        if(instruction == XOR_REG_LIT):
            reg = self.fetch()
            lit = self.fetch32()
            regvalue = self.getregister(reg)
            value = regvalue ^ lit
            self.setregister(ACC, value)
        if(instruction == XOR_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            regvalue1 = self.getregister(reg)
            regvalue2 = self.getregister(reg)
            value = regvalue1 ^ regvalue2
            self.setregister(ACC, value)
        if(instruction == NOT):
            reg = self.fetch()
            regvalue = self.getregister(reg)
            value = ~regvalue
            mask = 0xFFFFFFFF
            value = value & mask
            self.setregister(ACC, value)

        if(instruction == JNE_REG):
            reg = self.fetch()
            address = self.fetch32()
            regvalue = self.getregister(reg)
            if(regvalue != this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JNE_LIT):
            lit = self.fetch32()
            address = self.fetch32()
            if(lit != this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JEQ_REG):
            reg = self.fetch()
            address = self.fetch32()
            regvalue = self.getregister(reg)
            if(regvalue == this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JEQ_LIT):
            lit = self.fetch32()
            address = self.fetch32()
            if(lit == this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JGT_REG):
            reg = self.fetch()
            address = self.fetch32()
            regvalue = self.getregister(reg)
            if(regvalue > this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JGT_LIT):
            lit = self.fetch32()
            address = self.fetch32()
            if(lit > this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JLT_REG):
            reg = self.fetch()
            address = self.fetch32()
            regvalue = self.getregister(reg)
            if(regvalue < this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JLT_LIT):
            lit = self.fetch32()
            address = self.fetch32()
            if(lit < this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JGE_REG):
            reg = self.fetch()
            address = self.fetch32()
            regvalue = self.getregister(reg)
            if(regvalue >= this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JGE_LIT):
            lit = self.fetch32()
            address = self.fetch32()
            if(lit >= this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JLE_REG):
            reg = self.fetch()
            address = self.fetch32()
            regvalue = self.getregister(reg)
            if(regvalue <= this.getregister(ACC)):
                self.setregister(IP, address)
        if(instruction == JLE_LIT):
            lit = self.fetch32()
            address = self.fetch32()
            if(lit <= this.getregister(ACC)):
                self.setregister(IP, address)
            

            
        if(instruction == PRINT_REGISTERS):
            self.printallregisters();
        if(instruction == HALT):
            return True
        return False
            
    # Fetch and execute the next instruction
    def step(self):
        instruction = self.fetch();
        if(self.debug):
            p(instruction)
        return self.execute(instruction);
    # Main loop of the program
    def run(self):
        while not self.halt:
            self.halt = self.step()
        print('\r\n\r\ndone')

# Create and assign memory regions to the program
MemoryMap = MemoryMapper()
MemoryMap.map(bytearray(0x10000),0,0x10000,False)
my_screen = Screen()
MemoryMap.map(my_screen,0x9000,0x9100,False)

my_computer = computer(MemoryMap)

# Create the buffer with all the "code" in it
buffer = []

#Function to add the call to write a character to a string, to the buffer
def writeCharToScreen(char, x, y, command=0):
    temp = [MOV_LIT_MEM,char,x,y,command,0x00,0x00,0x90,0x00]
    for t in temp:
        buffer.append(t)

#Clear the screen
writeCharToScreen(0x20,0,0,0xff)

#Write a pattern with A's to the screen
c = 1
for x in range(0, 16):
    for y in range(0, 16):
        if(c):
            writeCharToScreen(0x41,x,y,4)
        else:
            writeCharToScreen(0x41,x,y,3)
        c=1-c
        
buffer += [HALT]

#Upload code at position 0
my_computer.upload_at_location(0,buffer)

# Step through the code one step at a time
my_computer.run()


my_screen.setRegular()
while 1: pass



