# Set up registers
R1 = 0
R2 = 1
R3 = 2
R4 = 3
ACC = 4
IP = 5
REGS = ['R1','R2','R3','R4','ACC','IP']


MOV_CONST_REG = 0x11   # Move constant into register
MOV_REG_REG = 0x12     # Move register into register
ADD_REG_REG = 0x20     # Add values from registers together into ACC
PRINT_REGISTERS = 0x30 # Print values of all registers

#Quick shortcut for printing
def p(inp):
    print(hex(inp))

#The entire computer class
class computer:
    def __init__(self):
        # Create a memory region for the registers
        # a 32 bit field (4 bytes) for every register
        self.registers = bytearray(6 * 4);
        # Create the RAM
        self.memory = bytearray(512)

    # Function for putting stuff in the memory
    def upload_at_location(self, location, buffer):
        for x in range(0, len(buffer)):
            self.memory[location+x] = buffer[x]

    # Quick way to debug what's going on
    def printallregisters(self):
        for x in range(0, 6*4, 4):
            print(REGS[int(x/4)] + ' 0x{:0<2x}{:0<2x}{:0<2x}{:0<2x}'.format(self.registers[x],self.registers[x+1],self.registers[x+2],self.registers[x+3]))

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
    
    # Execute the instruction passed to it
    def execute(self, instruction):
        if(instruction == MOV_CONST_REG):
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
            
    # Fetch and execute the next instruction
    def step(self):
        instruction = self.fetch();
        p(instruction)
        self.execute(instruction);



my_computer = computer()
# Create the buffer with all the "code" in it
buffer = [MOV_CONST_REG, 0x12, 0x34, 0x56, 0x78, R1,
          MOV_CONST_REG, 0x78, 0x56, 0x34, 0x12, R2,
          ADD_REG_REG, R1, R2,
          MOV_CONST_REG, 0x00, 0x00, 0x00, 0x00, R2,
          MOV_REG_REG, ACC, R1,
          PRINT_REGISTERS]

character_representation = ''.join([chr(x) for x in buffer])
print("LENGTH OF PROGRAM: {0} CHARACTERS".format(len(character_representation)))

#Upload code at position 0
my_computer.upload_at_location(0,buffer)

# Step through the code one step at a time
while 1:
    my_computer.step()
    i = input('>');
    if(i=='a'):
        my_computer.printallregisters()
