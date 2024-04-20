# Montgomery Ladder

This python script calculates equations of the form $$a^k \mod N$$ using
the [Montgomery ladder](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Montgomery_ladder).
It uses bit manipulation and masking to get the bit values at their respective index.

The Montgomery ladder method is more suited for cryptographic purposes than the _Square and Multiply_ method, which is
vulnerable to side-channel attacks (cf. [Colin D. Walter. Sliding Windows Succumbs to Big Mac Attack. (via psu.edu)](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=4db151eeda8c57f9e0fa2dc6ce7f44b674d24b82#page=272)).

## Usage
```shell
python3 montgomery_ladder.py 1234 2222 123
```
The above input calculates $$1234^{2222} \mod 123$$