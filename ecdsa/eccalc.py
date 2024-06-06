from dataclasses import dataclass
from logging import debug

def eea(a, b):
    if a == 0:
        return b, 0, 1

    gcd, temp1, temp2 = eea(b % a, a)

    temp3 = temp2 - (b // a) * temp1
    inverse = temp1

    return gcd, temp3, inverse


class FiniteField:
    __slots__ = ["module"]

    def __init__(self, module):
        self.module = module

    def add(self, a, b):
        return (a + b) % self.module

    def reduce(self, x):
        return x % self.module

    def multiply(self, a, b):
        return (a * b) % self.module

    def inverse(self, x):
        gcd, _, inverse = eea(self.module, x)

        if gcd != 1:
            raise ValueError(f'Cannot find an inverse of {x}')

        return inverse


@dataclass
class Point:
    x: int
    y: int
    infty: bool = False

    def __repr__(self):
        return "Infinity" if self.infty else f"({self.x:x}, {self.y:x})"


class EllipticCurve:
    def __init__(self, a, b, module):
        self.a = a
        self.b = b
        self.field = FiniteField(module)

    def hasPoint(self, p: Point) -> bool:
        return (p.y ** 2 - p.x ** 3 - self.a * p.x - self.b) % self.field.module == 0

    def addPoint(self, p: Point, q: Point):
        if p.x == 0 and p.y == 0 and p.infty:
            return q

        elif q.x == 0 and q.y == 0 and q.infty:
            return p

        elif p.x == q.x and p.y == self.field.reduce(-q.y):
            return Point(0, 0, True)

        elif p.x != q.x:
            dividor = self.field.add(q.x, -p.x)
            m = self.field.add(q.y, -p.y)
            m = self.field.multiply(m, self.field.inverse(dividor))

            u = self.field.add(self.field.multiply(m, m), -(q.x + p.x))
            v = self.field.add(self.field.multiply(m, self.field.add(u, -p.x)), p.y)
            return Point(u, self.field.reduce(-v))

        else:
            dividor = self.field.multiply(2, p.y)
            m = self.field.add(
                self.field.multiply(3, self.field.multiply(p.x, p.x)), self.a
            )
            m = self.field.multiply(m, self.field.inverse(dividor))

            u = self.field.add(self.field.multiply(m, m), -(2 * p.x))
            v = self.field.add(self.field.multiply(m, self.field.add(u, -p.x)), p.y)

            return Point(u, self.field.reduce(-v))

    def multiplyPoint(self, p: Point, n: int):
        h = p
        for i in range(n.bit_length() - 2, -1, -1):
            debug(f"{i=}:\tadding {h} and {h}")
            h = self.addPoint(h, h)
            if (n >> i) & 1:
                debug(f"\t\tadding {h} and {p} because bit is set")
                h = self.addPoint(h, p)
            debug(f"\t\th_{i}={h}")

        return h


@dataclass(frozen=True, slots=True)
class secp256r1(EllipticCurve):
    a = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    field = FiniteField(0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff)

    G = Point(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
              0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

    n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
