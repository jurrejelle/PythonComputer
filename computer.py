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


MOV_LIT_REG   = 0x11 # Move constant into register
MOV_REG_REG     = 0x12 # Move register into register
ADD_REG_REG     = 0x13 # Add values from registers together into ACC
PRINT_REGISTERS = 0x14 # Print values of all registers
PUSH_LIT        = 0x15 # Push a literal value to the stack
PUSH_REG        = 0x16 # Push a value from a register to the stack
POP             = 0x17 # Pop a value from the stack
CALL_LIT        = 0x18 # Make a call to a function whose pointer is a literal
CALL_REG        = 0x19 # Make a call to a function whose pointer comes from a register
RET             = 0x20 # Return back from a call instruction

#Quick shortcut for printing
def p(inp):
    print(hex(inp))

#The entire computer class
class computer:
    def __init__(self):
        # Create a memory region for the registers
        # a 32 bit field (4 bytes) for every register
        self.registers = bytearray(len(REGS) * 4);
        # Create the RAM
        self.memory = bytearray(512)


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
        if(instruction == ADD_REG_REG):
            reg1 = self.fetch()
            reg2 = self.fetch()
            value = self.getregister(reg1) + self.getregister(reg2)
            self.setregister(ACC, value)
        if(instruction == PRINT_REGISTERS):
            self.printallregisters();
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
            
    # Fetch and execute the next instruction
    def step(self):
        instruction = self.fetch();
        p(instruction)
        return self.execute(instruction);



my_computer = computer()
# Create the buffer with all the "code" in it
buffer = [PUSH_LIT, 0x41,0x41,0x41,0x41,
          PUSH_LIT, 0x42,0x42,0x42,0x42,
          PUSH_LIT, 0x43,0x43,0x43,0x43,
          
          PUSH_LIT,0x00,0x00,0x00,0x03,
          
          CALL_LIT,0x00,0x00,0x01,0x00,
          PRINT_REGISTERS
          ]


buffer2 = [RET]

#Upload code at position 0
my_computer.upload_at_location(0,buffer)
my_computer.upload_at_location(0x100,buffer2)

# Step through the code one step at a time
while 1:
    my_computer.step()
    i = input('>');
    if(len(i)>0):
        if(i=='a'):
            my_computer.printallregisters()
        if(i[0]=='m'):
            print(my_computer.memory)
        if(i[0]=='s'):
            print("STACK:")
            for x in range(my_computer.getregister(SP),508,4):
                print(hex(my_computer.fetch32at(x+4)))
            print("\n")
