class BasicLfsr:
    def __init__(self, bits):
        self.bits = bits

    def generate_next_bits(self):
        # Get the bit value of position 0 and 3
        bit_0 = (self.bits >> 0) & 1
        bit_3 = (self.bits >> 3) & 1

        # XOR operation result is 0b1
        # Shift it to the left with (length of the format - 1) times 
        # to get something like 0b1000.
        xor = ((bit_0 ^ bit_3) << 3)

        # Shift the bits to the right once
        return self.bits >> 1 | xor

    def stream(self):
        while True:
            next_bits = self.generate_next_bits()
            self.bits = next_bits
            yield self.bits


def test():
    test_case = [
        0b0110,
        0b0011,
        0b1001,
        0b0100,
        0b0010,
        0b0001,
        0b1000,
        0b1100,
        0b1110,
        0b1111,
        0b0111,
        0b1011,
        0b0101,
        0b1010,
        0b1101,
        0b0110
    ]
    
    initial_state = 0b0110


    lfsr = BasicLfsr(initial_state)
    gen = lfsr.stream()

    current = initial_state

    i=0
    while i < 20:
        print(format(current, '04b')) 
        if i < len(test_case):
            if current != test_case[i]:
                raise Exception(f"Failed at t - {i}: {format(current, '04b')} != {format(test_case[i], '04b')}")

        current = next(gen)
        i+=1
    
test()
