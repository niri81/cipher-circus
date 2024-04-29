package hash

import (
	"encoding/binary"
	"fmt"
	"log"
	"math/bits"
)

func Q(input uint32) uint32 {
	return input ^ bits.RotateLeft32(input, 17)
}

func H(input string) uint32 {
	internalState := uint32(0x524f464c)
	bytes := []byte(input)

	buffer := make([]byte, 4)

	for i := 0; i < len(bytes); i += 4 {
		remaining := len(bytes) - i
		if remaining < 4 {
			buffer = bytes[i : i+4]
		} else {
			buffer = bytes[i : i+remaining]
			for j := range len(bytes) - 4 {
				bytes[j] = 0xff
			}
		}
		internalState = Q(internalState ^ binary.LittleEndian.Uint32(buffer))
	}

	return Q(internalState)
}

func AssertEqual[T comparable](actual, expected T) {
	if actual != expected {
		log.Fatal(fmt.Sprintf("got: %x; want: %x", actual, expected))
	}
}

func test() {
	AssertEqual(Q(uint32(0x524f464c)), 0xded7e2d2)
	AssertEqual(Q(Q(uint32(0x524f464c))), 0x1b725f7d)
	AssertEqual(Q(Q(Q(uint32(0x524f464c)))), 0xa5886999)
	println("All tests of the static hash function Q succeeded")

	AssertEqual(H(""), 0xded7e2d2)
	AssertEqual(H("A"), 0x5d725f7f)
	AssertEqual(H("AB"), 0x5f3b5f7f)
	AssertEqual(H("ABC"), 0x5f39137f)
	AssertEqual(H("ABCD"), 0x5f391128)
	AssertEqual(H("ABCDE"), 0x2f69af58)
	println("All tests of the hash function H succeeded")

	println("All tests ran successfully")
}

func main() {
	test()
}
