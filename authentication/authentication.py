class HexString(str):
    """
    Extends the string class to be able to process XORs
    """

    def __xor__(self, other):
        return HexString(hex(int(self, 16) ^ int(other, 16)))


class Buffer:
    """
    Handles the read and writes to the buffer
    """
    state: HexString = ""

    def writeBuffer(self, hex_content: HexString):
        """
        Handles writes to the buffer
        :param hex_content: hex content that should be written to the buffer
        :return:
        """
        self.state = hex_content

    def readBuffer(self) -> HexString:
        """
        Handles reads from the buffer
        :return: buffer state
        """
        return self.state

    def clearBuffer(self):
        """
        Clears the buffer
        """
        self.state = HexString("")


class Authentication:
    """
    Handles the authentication function
    """
    internalState: HexString = "0x524f464c"  # LOL

    def reset(self):
        """
        For resetting the internal state of the function
        """
        self.internalState = HexString("0x524f464c")

    @staticmethod
    def rotateLeft(b: int) -> HexString:
        """
        Rotates the given bit-sequence left by 17 bits
        :param b: input integer
        :return: rotated hex string
        """
        return HexString(hex(((b << 17) | (b >> (32 - 17))) & 0xFFFFFFFF))

    def Q(self, b: HexString) -> HexString:
        """
        Implemented static hash function Q
        :param b: input hex string
        :return: hash result hex string
        """
        return b ^ (self.rotateLeft(int(b, 16)))

    def handleFilledBuffer(self, buffer: Buffer):
        """
        Handles a full buffer and executes defined methods
        :param buffer: Buffer object
        """
        content = buffer.readBuffer()
        self.internalState = self.Q(HexString(content) ^ HexString(self.internalState))
        buffer.clearBuffer()

    def H(self, hex: HexString) -> HexString:
        """
        Hash function that takes the input
        :param hex:
        :return:
        """
        buffer = Buffer()

        if len(hex) == 0:
            return self.Q(HexString(self.internalState))

        if (l := len(hex) % 8) != 0:
            hex += "f" * (8 - l)

        for data in [hex[i:i + 8] for i in range(0, len(hex), 8)]:
            buffer.writeBuffer(HexString(data))
            self.handleFilledBuffer(buffer)

        return self.Q(self.internalState)

    def test(self):
        """
        Tests the implemented functions with the given values
        """
        assert self.Q(HexString(self.internalState)) == "0xded7e2d2"
        assert self.Q(self.Q(HexString(self.internalState))) == "0x1b725f7d"
        assert self.Q(self.Q(self.Q(HexString(self.internalState)))) == "0xa5886999"
        assert self.H(HexString("".encode().hex())) == "0xded7e2d2"
        self.reset()
        assert self.H(HexString("A".encode().hex())) == "0x5d725f7f"
        self.reset()
        assert self.H(HexString("AB".encode().hex())) == "0x5f3b5f7f"
        self.reset()
        assert self.H(HexString("ABC".encode().hex())) == "0x5f39137f"
        self.reset()
        assert self.H(HexString("ABCD".encode().hex())) == "0x5f391128"
        self.reset()
        assert self.H(HexString("ABCDE".encode().hex())) == "0x2f69af58"
        self.reset()
        print("All tests passed")
        print()


auth = Authentication()
print("Testing code...")
auth.test()

print("Proceeding to Length Extension Attack...")
# The following code uses hex values from the Go Code (speed :D)
# candidates = [0x332e2800, 0xccd1d7ff]

candidate = HexString("ccd1d7ff")

assert auth.Q(candidate) == "0x632e4e5c"
print("MIC for abcd: ", auth.Q(candidate))

assert auth.Q(auth.Q(candidate ^ b"ef\xff\xff".hex())) == "0xf6b8802"
print("MIC for abcdef: ", auth.Q(auth.Q(candidate ^ b"ef\xff\xff".hex())))

assert auth.Q(auth.Q(auth.Q(candidate ^ b"efgh".hex()) ^ b"ijk\xff".hex())) == "0x2638a819"
print("MIC for abcdefghijk: ", auth.Q(auth.Q(auth.Q(candidate ^ b"efgh".hex()) ^ b"ijk\xff".hex())))

# Own message: abcdROFL (I can use ROFL too)
print("MIC for abcdROFL: ", auth.Q(auth.Q(candidate ^ b"ROFL".hex())))
