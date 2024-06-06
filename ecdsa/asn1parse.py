from abc import ABC, abstractmethod


class ASN1Object(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __bytes__(self):
        pass

    @abstractmethod
    def __int__(self):
        pass


class Sequence(ASN1Object):
    def __init__(self, content: list):
        self.content = content

    def __bytes__(self):
        output = b""
        for content in self.content:
            output += bytes(content)
        return b"\x30" + (len(output)).to_bytes(1, 'big') + output

    def __str__(self):
        content = ""
        for i in self.content:
            content += str(i) + ","
        return f"Sequence({content[:-1]})"

    def __int__(self):
        raise TypeError("Sequence cannot be converted to integer")

    def get(self, index: int) -> ASN1Object | None:
        if index >= len(self.content):
            return None
        return self.content[index]


class Integer(ASN1Object):
    def __init__(self, value: int | bytes):
        if isinstance(value, int):
            self.value = value
        else:
            self.value = int.from_bytes(value, "big")

    def __bytes__(self):
        byte_length = (self.value.bit_length() + 8) // 8

        # check if MSB set
        if self.value >> byte_length * 8 == 1:
            byte_length += 1
        return b"\x02" + byte_length.to_bytes(1, byteorder='big') + self.value.to_bytes(byte_length, 'big')

    def __str__(self):
        return f"Integer({self.value})"

    def __eq__(self, other):
        if not isinstance(other, Integer):
            raise TypeError(f"Cannot compare {type(self)} to {type(other)}")
        return self.value == other.value

    def __int__(self):
        return self.value


class ASN1ParseException(Exception):
    def __init__(self, message):
        self.message = message


class ASN1Parser:
    """
    Allows parsing of sequences and integers for any arbitrary depth
    """
    asn1_types = {"0x2": Integer, "0x30": Sequence}
    tree = {}

    def parse(self, byte_input: bytes):
        packed = False
        current_index = 0
        content = []
        while current_index < len(byte_input):
            if not (current_type := self.asn1_types.get(hex(byte_input[current_index]))):
                raise ASN1ParseException(f"Unknown ASN1 type found")
            if current_type == Sequence and current_index == 0:
                packed = True
                current_index += 2
            elif current_type == Sequence:
                length = byte_input[current_index + 1]
                current_index += 2
                content.append(Sequence(self.parse(byte_input[current_index:current_index + length])))
                current_index += length
            else:
                length = byte_input[current_index + 1]
                current_index += 2
                content.append(Integer(byte_input[current_index:current_index + length]))
                current_index += length
        if packed:
            return Sequence(content)
        else:
            return content


# Some tests
if __name__ == "__main__":
    int1 = bytes(Integer(3))
    int2 = bytes(Integer(16))
    int3 = bytes(Integer(127))
    int4 = bytes(Integer(128))
    seq = bytes(Sequence([Integer(3), (Integer(255)), Sequence([Integer(127), Sequence([Integer(22)])]), Integer(128)]))

    print(seq)

    parser = ASN1Parser()
    print(parser.parse(int1))
    print(parser.parse(int2))
    print(parser.parse(int3))
    print(parser.parse(int4))
    print(parser.parse(seq))
