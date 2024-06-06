from dataclasses import dataclass


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
        if x == 1:
            return 1
        for i in range(2, self.module):
            if self.multiply(x, i) == 1:
                return i
        raise ValueError(f"Cannot find inverse for {x}")


@dataclass
class Point:
    x: int
    y: int
    infty: bool = False

    def __repr__(self):
        return "Infinity" if self.infty else f"({self.x}, {self.y})"


class EllipticCurve:
    def __init__(self, a, b, module):
        self.a = a
        self.b = b
        self.field = FiniteField(module)

    def hasPoint(self, p: Point, debug=False) -> bool:
        if debug:
            print(f"{p.y ** 2 + p.x * p.y + p.x ** 3 + p.x ** 2 * self.a + self.b=}")
        return (p.y**2 - p.x**3 - self.a * p.x - self.b) % self.field.module == 0

    def addPoint(self, p: Point, q: Point, debug=False):
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

            if debug:
                print(f"\t\t{m=}")

            u = self.field.add(self.field.multiply(m, m), -(q.x + p.x))
            v = self.field.add(self.field.multiply(m, self.field.add(u, -p.x)), p.y)
            return Point(u, self.field.reduce(-v))

        else:
            dividor = self.field.multiply(2, p.y)
            m = self.field.add(
                self.field.multiply(3, self.field.multiply(p.x, p.x)), self.a
            )
            m = self.field.multiply(m, self.field.inverse(dividor))

            if debug:
                print(f"\t\t{m=}")

            u = self.field.add(self.field.multiply(m, m), -(2 * p.x))
            v = self.field.add(self.field.multiply(m, self.field.add(u, -p.x)), p.y)

            return Point(u, self.field.reduce(-v))

    def multiplyPoint(self, p: Point, n: int, debug=False):
        h = p
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


el = EllipticCurve(1, 679, 1151)
p = Point(501, 449)
k_pra = 199
k_prb = 211

k_puba = el.multiplyPoint(p, k_pra, True)
print("Public Key Alice:", k_puba)

print("\n")

k_pubb = el.multiplyPoint(p, k_prb, True)
print("Public Key Bob:", k_pubb)

print("\n")

shared_key = el.multiplyPoint(k_pubb, k_pra, True)
assert shared_key == el.multiplyPoint(k_puba, k_prb)

print("Shared Key:", shared_key)

assert shared_key == el.multiplyPoint(k_pubb, k_pra)
assert el.hasPoint(shared_key)
