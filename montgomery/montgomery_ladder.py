import argparse
import math


def ladder(a: int, k: int, N: int, debug=False) -> int:
    """
    Calculates the given term using the montgomery ladder algorithm
    :param a: base
    :param k: exponent
    :param N: finite body
    :return:
    """
    x = 1
    y = a % N

    if debug:
        print("Step 0: x =", x, ", y =", y)

    # Get bit length l of k (using log2) and generate a list [l, l-1, ..., 1, 0] that is then iterated
    for i in range(math.ceil(math.log(k, 2)) - 1, -1, -1):
        # Shift k right by i (get i-th bit) and check if it is 0
        if (k >> i) & 0x01 == 0:
            y = (x * y) % N
            x = (x * x) % N
        # i-th bit is 1
        else:
            x = (x * y) % N
            y = (y * y) % N

        # Print out step overview
        if debug:
            print(f"After Step {math.ceil(math.log(k, 2)) - i}: i = {i}, x = {x}, y = {y}, b_i was: {(k >> i) & 0x01}")

    return x


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Montgomery ladder algorithm of the form: a^k mod N')
    parser.add_argument('a', type=int, help='base')
    parser.add_argument('k', type=int, help='exponent')
    parser.add_argument('N', type=int, help='finite body')

    args = parser.parse_args()
    print(f"\nFinal result is: {ladder(args.a, args.k, args.N)}")
