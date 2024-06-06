from eccalc import secp256r1, FiniteField
from asn1parse import ASN1Parser, Sequence, Integer
from hashlib import sha256


class ECDSA:
    @staticmethod
    def sign(d: int, m: str, k: int) -> Sequence:
        curve = secp256r1()
        field = FiniteField(curve.n)

        e = int.from_bytes(sha256(bytes(m, 'utf-8')).digest(), byteorder='big')

        R = curve.multiplyPoint(secp256r1.G, k)

        r = Integer(R.x)
        s = Integer((e + R.x * d) * field.inverse(k) % field.module)

        return Sequence([r, s])

    @staticmethod
    def __calculate_nonce(seq1: Sequence, seq2: Sequence, m1: str, m2: str):
        curve = secp256r1
        field = FiniteField(curve.n)

        e1 = int.from_bytes(sha256(bytes(m1, 'utf-8')).digest(), byteorder='big')
        e2 = int.from_bytes(sha256(bytes(m2, 'utf-8')).digest(), byteorder='big')

        if not seq1.get(0) == seq2.get(0):
            raise AttributeError("S1 and S2 are not equal, private key cannot be determined")

        if not seq1.get(0) or not seq1.get(1) or not seq2.get(1):
            raise AttributeError("Could not load required values from signature")

        r = int(seq1.get(0))
        s1 = int(seq1.get(1))
        s2 = int(seq2.get(1))

        d = (s2 * e1 - s1 * e2) * field.inverse(s1 * r - s2 * r) % field.module

        return d

    @staticmethod
    def determine_nonce_reuse(seq1: bytes, seq2: bytes, m1=None, m2=None):
        parser = ASN1Parser()
        seq1 = parser.parse(seq1)
        seq2 = parser.parse(seq2)

        if seq1.get(0) and seq2.get(0) and seq1.get(0) == seq2.get(0):
            print("Nonce reuse")
            if m1 and m2:
                print("Determining private key... One sec, boss")
                private_key = ECDSA.__calculate_nonce(seq1, seq2, m1, m2)
                print(f"Private Key is: hex: 0x{private_key:x} or int: {private_key} or bitstring: {bin(private_key)} or {bytes.fromhex(hex(private_key)[2:])}")
        else:
            print("No nonce reuse")
