import argparse
import timeit
from hashlib import md5
import random
import string


def H(input_text: str) -> str:
    """
    Calculates the MD5 hash of a given string and returns its first 32 bits
    :param str input_text:
    :return: Hash value consisting of the first 32 bits of the MD5 hash
    """
    return md5(input_text.encode()).hexdigest()[:8]


def testHashFunction() -> None:
    """
    Performs test of the hash function using the given examples
    """
    print("Testing 'super secure' hash function with given values:")
    print(f"\t{H('')=}")
    assert H('') == 'd41d8cd9'
    print(f"\t{H('Leeroy Jenkins')=}")
    assert H('Leeroy Jenkins') == 'eddda4a6'
    print("\n")


def generateMessageText(prefix: str, length: int) -> str:
    """
    Generates a random string of given length using ASCII characters and digits
    :param str prefix: String prefix for the message
    :param int length: Length of the string to generate
    :return: Generated string
    """
    return prefix + "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generateCollision(prefix: str, message_length: int) -> None:
    """
    Brute-force algorithm to generate a hash collision
    :param str prefix: Prefix for the message
    :param int message_length: Length of the message used for hashing
    """
    print("Searching for hash collisions:")
    hash_table = dict()

    start = timeit.default_timer()
    i = 0
    generated_text = generateMessageText(prefix, message_length)
    generated_hash = H(generated_text)

    while generated_hash not in hash_table.keys():
        hash_table[generated_hash] = generated_text
        i += 1
        generated_text = generateMessageText(prefix, message_length)
        generated_hash = H(generated_text)

    end = timeit.default_timer()

    print(f"\t{generated_text}\t—\t{generated_hash}")
    message = hash_table[generated_hash]
    print(f"\t{message}\t—\t{H(message)}\n")
    print(f"This collision was found after {i} iterations and in {end - start} seconds")


def main():
    """
    Main method that parses the command line arguments, tests the hash function and generates a hash collision
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", help="Prefix for the message", required=True)
    parser.add_argument("-l", "--message_length", type=int, help="Length of the message used for hashing", default=64)

    args = parser.parse_args()
    testHashFunction()
    generateCollision(args.prefix, args.message_length)


if __name__ == "__main__":
    main()