import copy
from dataclasses import dataclass
from logging import debug


@dataclass(frozen=True, slots=True)
class GaloisField:
    polynomial: int
    module_exponent: int


class FieldElement:
    def __init__(self, value: int, field: GaloisField):
        self.field = field
        self.value = value

    def __add__(self, other):
        temp = copy.deepcopy(self)
        temp.value ^= other.value
        return temp

    def __sub__(self, other):
        return self + other

    def __mul__(self, other):
        temp = FieldElement(0, self.field)
        if isinstance(other, int):
            debug(f"Multiplying {self.value} with {other}")
            for i in range(other):
                temp += self
            return temp

        if not isinstance(other, FieldElement):
            raise TypeError

        for i in range(other.value.bit_length(), -1, -1):
            if (other.value >> i) & 1:
                debug(f"Bit {i} is set, proceeding with leftshift")
                temp.value ^= self.value << i
                debug(f"temp after leftshift is {temp.value:b}")
            while temp.value >> self.field.module_exponent > 0:
                debug("need reducing")
                debug(
                    f"reducing with {self.field.polynomial << (temp.value.bit_length() - 1 - self.field.module_exponent):b}"
                )
                temp.value ^= self.field.polynomial << (
                    temp.value.bit_length() - 1 - self.field.module_exponent
                )
                debug(f"temp after reducing is {temp.value:b}")
        return temp

    def __pow__(self, power, modulo=None):
        temp = copy.deepcopy(self)
        for i in range(power - 1):
            temp *= self
        return temp

    def __eq__(self, other):
        if isinstance(other, FieldElement):
            return other.value == self.value
        if isinstance(other, int):
            return self.value == other
        raise TypeError

    def __repr__(self):
        set_bits = []
        if self.value == 0:
            return "0"

        for i in reversed(range(self.value.bit_length())):
            if (self.value >> i) & 1:
                if i == 0:
                    set_bits.append("1")
                else:
                    set_bits.append(f"a^{i}")
        return "+".join(set_bits)

    def invert(self):
        if self.value == 1:
            return FieldElement(1, self.field)
        for i in range(2, 2**self.field.module_exponent):
            element = FieldElement(i, self.field)
            if self * element == 1:
                return element
        raise ValueError(f"Cannot invert {self.value}")


class Point:
    def __init__(self, x, y, field, infty=False):
        if isinstance(x, FieldElement):
            self.x = x
        else:
            self.x = FieldElement(x, field)

        if isinstance(y, FieldElement):
            self.y = y
        else:
            self.y = FieldElement(y, field)

        self.infty = infty

    def __repr__(self):

        return "Infinity" if self.infty else f"({self.x}, {self.y})"

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y


class EllipticCurve:
    def __init__(self, a, b, module_exponent, polynomial):
        self.field = GaloisField(polynomial, module_exponent)
        self.a = FieldElement(a, self.field)
        self.b = FieldElement(b, self.field)

    def hasPoint(self, p: Point, debug=False) -> bool:
        if debug:
            print(f"{p.y ** 2 + p.x * p.y + p.x ** 3 + p.x ** 2 * self.a + self.b=}")
        return p.y**2 + p.x * p.y + p.x**3 + p.x**2 * self.a + self.b == 0

    def addPoint(self, p: Point, q: Point, debug=False):
        null = FieldElement(0, self.field)
        if p.x == 0 and p.y == 0 and p.infty:
            return q

        elif q.x == 0 and q.y == 0 and q.infty:
            return p

        elif p.x == q.x and p.y == q.x + q.y:
            return Point(null, null, self.field, True)

        elif p.x == q.x and p.y == p.x + p.y:
            return Point(null, null, self.field, True)

        elif p.x != q.x:
            dividor = q.x + p.x
            m = q.y + p.y
            m = m * dividor.invert()

            if debug:
                print(f"\t\t{m=}")

            u = m**2 + m + self.a + p.x + q.x
            v = m * (u + p.x) + u + p.y
            return Point(u, v, self.field)

        else:
            m = p.x + p.y * p.x.invert()

            if debug:
                print(f"\t\t{m=}")

            u = m**2 + m + self.a
            v = m * (p.x + u) + u + p.y
            return Point(u, v, self.field)

    def multiplyPoint(self, p: Point, n: int, debug=False):
        h = copy.deepcopy(p)
        for i in range(n.bit_length() - 2, -1, -1):
            if debug:
                print(f"{i=}:\tadding {h} and {h}")
            h = self.addPoint(h, h, debug)
            if debug:
                print(f"\t\tis: {h=}")
            if (n >> i) & 1:
                if debug:
                    print(f"\t\tadding {h} and {p} because bit is set")
                h = self.addPoint(h, p, debug)
            if debug:
                print(f"\t\th_{i}={h}")
        return h

    def findOrder(self, p: Point, elements: int, debug=False):
        if p.infty:
            return 1
        # Testing all possible orders to be able to use more curves
        # Normally, one would only test 1, 2, 11, 22
        for i in range(2, 2**self.field.module_exponent):
            if elements % i != 0:
                continue
            if self.multiplyPoint(p, i, debug).infty:
                return i
            print(f"ord(P) != {i}")
        raise ValueError


# logging.basicConfig(level=logging.DEBUG)

el = EllipticCurve(0xA, 0xD, 4, 0x13)

p = Point(0xC, 0xA, el.field)

print(f"P liegt auf E: {el.hasPoint(p, True)}")
print()

print(f"ord(P) = {el.findOrder(p, 22, True)}")
print()

k_pra = 7
k_prb = 5

k_puba = el.multiplyPoint(p, k_pra, True)
print("Public Key Alice:", k_puba)

print("\n")

k_pubb = el.multiplyPoint(p, k_prb, True)
print("Public Key Bob:", k_pubb)

print("\n")

shared_key = el.multiplyPoint(k_pubb, k_pra, True)
assert shared_key == el.multiplyPoint(k_puba, k_prb, True)

print("Shared Key:", shared_key)

assert shared_key == el.multiplyPoint(k_pubb, k_pra)
assert el.hasPoint(shared_key)
