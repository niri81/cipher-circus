#!/usr/bin/env python3

import math
from base64 import b64decode
from hashlib import sha256
import argparse
from dataclasses import dataclass

# following only used for parsing private key from PEM
from pyasn1.codec.der import decoder
from pyasn1_modules import rfc5958, rfc8017


def new_bytes(x: int) -> bytes:
    return x.to_bytes(math.ceil(x.bit_length() / 8), 'big')


def bytes_xor(a: bytes, b: bytes):
    return new_bytes(int.from_bytes(a, 'big') ^ int.from_bytes(b, 'big'))


@dataclass(frozen=True, slots=True)
class RSA_PrivateKey:
    n: int
    d: int


class RSA_OAEP:
    SEED_LENGTH = 64 // 8

    def mgf_1_sha256(self, mgfSeed: bytes, maskLen: int) -> bytes:
        """
        Mask Generating Function 1 using SHA256 as specified in NIST SP 800-56B Rev. 2 7.2.2.2

        :param mgfSeed: MGF Seed that is used for generating the mask
        :param maskLen: Required mask length in bytes
        :return: Mask
        """
        if maskLen > 2 ** 32 * self.SEED_LENGTH:
            raise ValueError('Mask length too large for available hash function')

        t = b""

        for counter in range(0, math.ceil(maskLen // self.SEED_LENGTH)):
            counter_bytes = int.to_bytes(counter, 4, byteorder='big')
            t += sha256(mgfSeed + counter_bytes).digest()

        return t[:maskLen]

    def decrypt(self, key: RSA_PrivateKey, C: bytes, A: bytes, **kwargs) -> str | bytes:
        """
        Performs RSA-OAEP decryption using the provided RSA private key as specified in NIST SP 800-56B Rev. 2 7.2.2.4

        :param key: RSA Private Key object
        :param C: Ciphertext bytes
        :param A: Additional information that is to be authenticated
        :return: Decrypted bytes
        """

        # 1. Initialization
        nLen = key.n.bit_length() // 8
        decryptErrorFlag = False

        # 2. Check for erroneous input
        if len(C) != nLen:
            raise ValueError('Length of C does exceed the module length')

        c = int.from_bytes(C, byteorder='big')

        if not (1 < c < key.n - 1):
            raise ValueError('C is too large for module length')

        # 3. RSA Decryption
        em = pow(c, key.d, key.n)

        # 4. OAEP decoding
        # ha = sha256(A).digest() not necessary due to BauerRFC but necessary in normal implementation

        # Shift integers to get the data
        y = em >> 8 * (nLen - 1)

        maskedMgfSeed = new_bytes((em & (2 ** (8 * (nLen - 1)) - 1)) >> 8 * (nLen - self.SEED_LENGTH - 1))
        maskedDb = new_bytes(em & 2 ** (8 * (nLen - self.SEED_LENGTH - 1)) - 1)

        mgfSeedMask = self.mgf_1_sha256(maskedDb, self.SEED_LENGTH)
        mgfSeed = bytes_xor(maskedMgfSeed, mgfSeedMask)

        if not len(mgfSeed) == self.SEED_LENGTH:
            mgfSeed = b"\00" * (self.SEED_LENGTH - len(mgfSeed)) + mgfSeed

        dbMask = self.mgf_1_sha256(mgfSeed, nLen - self.SEED_LENGTH - 1)

        DB = bytes_xor(maskedDb, dbMask)

        HA = DB[:self.SEED_LENGTH * 4]
        X = DB[self.SEED_LENGTH * 4:]

        # 5. Check for RSA-OAEP decryption errors
        if not y == 0:
            decryptErrorFlag = True

        if not (one_byte_position := X.index(b'\01')):
            decryptErrorFlag = True
        elif not X.startswith(b'\00' * one_byte_position):
            decryptErrorFlag = True

        # 6. Output of the decryption process

        output = X[X.find(b'\x01') + 1:]

        # This is different from the NIST recommendation but acc. to BauerRFC8017
        if not HA == sha256(output).digest():
            decryptErrorFlag = True

        if decryptErrorFlag:
            raise Exception('Decryption failed')

        print("Decryption successful:")

        if kwargs["decode"]:
            return output.decode(kwargs["decode"])
        return output


# run via "./decrypt.py -k privkey.pem -d utf-8 ciphertext_self.bin"
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A RSA-OAEP decryption utility")
    parser.add_argument('-k', '--key', help="RSA Private Key file", required=True)
    parser.add_argument("-d", "--decode", type=str, help="Decode output",
                        choices=["utf-16", "utf-8", "ascii"], default=False)
    parser.add_argument('-a', '--additional', help="Additional information that is to be authenticated given in utf-8",
                        default="", type=str)
    parser.add_argument("file", help="The input file to decrypt, given as bin file")

    args = parser.parse_args()

    try:
        # parsing the private key provided
        with open(args.key, "rb") as f:
            read_content = b64decode(b''.join(f.readlines()[1:-1]))
            decoded, _ = decoder.decode(read_content, asn1Spec=rfc5958.PrivateKeyInfo())
            private_key = decoder.decode(decoded['privateKey'], asn1Spec=rfc8017.RSAPrivateKey())
            key = RSA_PrivateKey(int(private_key[0]['modulus']), int(private_key[0]['privateExponent']))
        # loading the file and running the decryption process
        with open(args.file, 'rb') as f:
            oaep = RSA_OAEP()
            print(oaep.decrypt(key, f.read(), bytes(args.additional, 'utf-8'), decode=args.decode))

    except FileNotFoundError:
        print("File could not be found")
