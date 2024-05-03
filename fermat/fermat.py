import argparse
import math
from montgomery import montgomery_ladder


def fermat(p: int):
    """
    Executes Fermat test on a given number p using the montgomery ladder for powers of p
    :param p: Number to test
    """
    for a in range(2, p):  # For all numbers a=2,...,p-1
        if (
                gcd := math.gcd(a,
                                p)) != 1:  # If gcd is > 1, they share a common divider and can not be used for a Fermat test
            print(f"{a} will not be used, because gcd(a,p) = {gcd}")
            continue

        if (
                result := montgomery_ladder.ladder(a, p - 1,
                                                   p)) != 1:  # Calculates a^(p-1) mod p and checks if result is !=1
            print(f"{p} is a compound number, because {a}^{p - 1} = {result} mod {p}")  # If !=1, p is a compound number
            return
        print(f"{a}^{p - 1} = 1 mod {p}")
    print(f"{p} is a prime or a compound number")  # If a^(p-1) == 1 mod p forall a=2,...,p-1


if __name__ == "__main__":
    # Some argument parsing to allow for easier script execution
    parser = argparse.ArgumentParser(description="Executes Fermat Test")
    parser.add_argument("p", type=int, help="Number to carry out Fermat test on")

    args = parser.parse_args()
    fermat(args.p)
