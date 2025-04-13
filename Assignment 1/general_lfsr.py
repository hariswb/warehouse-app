class GeneralLfsr:
    def __init__(self, register_size, taps, bits):
        """
        Tap sequence should be in bitmask form.
        I.e., tap sequence of 0 and 3 index in register size of 4
        would be defined as 0b1001.
        Likewise, tap sequence of 1, 3, and 4 in register size of 5
        would be defined as 0b11010
        """
        self.register_size = register_size
        self.taps= self.fit_to_register_size(taps, "Tap sequence")
        self.bits = self.fit_to_register_size(bits, "Bits")

    def fit_to_register_size(self, bits, component_name):
        bin_str = bin(bits).lstrip('0b')  # remove '0b' prefix
        if len(bin_str) <= self.register_size:
            return bits
        else:
            raise Exception(f"{component_name} {bin(bits)} doesn't fit the register size of {self.register_size}")

    def set_register_size(self, register_size):
        self.register_size = register_size

    def generate_next_bits(self):
        # Shift the bits to the right once
        next_bits = self.bits >> 1

        xor = self.xor_taps()

        return next_bits | xor
    
    def xor_taps(self):
        """
        Tap the tap sequence into the current state, then
        iterate each individual bit with XOR operation.
        Iteration stops after the tapped_bits reach 0.
        """
        tapped_bits = self.bits & self.taps
        xor = 0
        while tapped_bits:
            xor ^= (tapped_bits & 1)
            # Shift the bits to the right
            tapped_bits >>= 1
        
        # XOR operation result is 0b1
        # Shift it to the left with (register_size - 1) times 
        # to get something like 0b1000...
        return xor << self.register_size - 1

    def stream(self):
        while True:
            next_bits = self.generate_next_bits()
            self.bits = next_bits
            yield self.bits

    def format_str(self, bits):
        return format(bits, f'0{self.register_size}b')

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
        0b0110,
        0b0011,
        0b1001,
        0b0100,
        0b0010,
    ]
    lfsr = GeneralLfsr(4, 0b1001, 0b0110)

    current = lfsr.bits

    gen = lfsr.stream()
    i = 0
    while i < len(test_case):
        print(lfsr.format_str(current)) 
        if current != test_case[i]: 
            raise Exception(f"Failed at t-{i}. {bin(next_bits)} != {bin(test_case[i])}")

        current = next(gen)
        i+=1

test()
