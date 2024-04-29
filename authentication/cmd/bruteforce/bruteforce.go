package main

import (
	"fmt"
	"github.com/niri81/cipher-circus/authentication/pkg/hash"
	"math"
)

func findLastState(lookup uint32) []uint32 {
	var foundCandidates []uint32
	var maxI = uint32(0xffffffff)
	for i := uint32(0); i < maxI; i++ {
		hash.Q(i)
		if hash.Q(i) == lookup {
			foundCandidates = append(foundCandidates, i)
			println(fmt.Sprintf("Found candidate 0x%x during last state lookup for value 0x%x", i, lookup))
			// return foundCandidates // Remove this line for finding all candidates
		}
	}

	return foundCandidates
}

func findCandidate(lookup uint32) []uint32 {
	var foundCandidates []uint32
	var maxI = uint32(math.Pow(2, 32) - 1)

	for i := uint32(0); i < maxI; i++ {
		if hash.Q(i) == lookup {
			foundCandidates = append(foundCandidates, i)
			println(fmt.Sprintf("Found candidate 0x%x during lookup for value 0x%x", i, lookup))
		}
	}

	return foundCandidates
}

func main() {
	var searchedLastState = uint32(0x632e4e5c)                // Output of H('abcd')
	var potentialLastState = findLastState(searchedLastState) // Do a bruteforce to find a value that produces this state

	for _, candidate := range potentialLastState {
		hash.AssertEqual(searchedLastState, hash.Q(candidate))
		fmt.Printf("Candidate 0x%x confirmed\n", candidate)
	}
}
