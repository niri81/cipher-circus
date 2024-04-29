package main

import "math/bits"

func Q(input uint32) uint32 {
	return input ^ (bits.RotateLeft32(input, 17))
}

func h(input string) {

}

func main() {

}
