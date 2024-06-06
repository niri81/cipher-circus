from ecdsa import ECDSA
from secrets import randbits


def task1and2():
    with open('signature.bin', 'wb') as f:
        print("Task1+2:")
        content = bytes(ECDSA.sign(0xd9c73e5dcfbf0e5b04dfdd261ff597b2a9098af481d321cdf156f0d7bd7791b1,
                                   "superTolleTestNachricht", randbits(256)))
        print(f"Calculated signature content as: 0x{content.hex()}")
        print("Writing to file signature.bin")
        f.write(content)
        print("\n")


def task3():
    print("Task3:")
    with open('bauer_spezial/signature1.bin', 'rb') as f:
        sig1 = f.read()

    with open('bauer_spezial/message1.bin') as f:
        cont1 = f.read()

    with open('bauer_spezial/signature2.bin', 'rb') as f:
        sig2 = f.read()

    with open('bauer_spezial/message2.bin') as f:
        cont2 = f.read()

    ECDSA.determine_nonce_reuse(sig1, sig2, cont1, cont2)
    print("\n")


def task4():
    print("Task4:")
    nonce = randbits(256)

    print(f"Creating messages in directory my_messages...")
    with open('my_messages/message1.bin') as f:
        cont = f.read()

    with open('my_messages/signature1.bin', 'wb') as f:
        f.write(bytes(
            ECDSA.sign(0x68747470733a2f2f796f7574752e62652f78786e6831437752634f67, cont, nonce)
        ))

    with open('my_messages/message2.bin') as f:
        cont = f.read()

    with open('my_messages/signature2.bin', 'wb') as f:
        f.write(bytes(
            ECDSA.sign(0x68747470733a2f2f796f7574752e62652f78786e6831437752634f67, cont, nonce)
        ))
    print("Done")
    print("\n")


def task4_check():
    print("Checking generated signatures for own messages")
    with open('my_messages/signature1.bin', 'rb') as f:
        sig1 = f.read()

    with open('my_messages/message1.bin') as f:
        cont1 = f.read()

    with open('my_messages/signature2.bin', 'rb') as f:
        sig2 = f.read()

    with open('my_messages/message2.bin') as f:
        cont2 = f.read()

    ECDSA.determine_nonce_reuse(sig1, sig2, cont1, cont2)


if __name__ == '__main__':
    task1and2()
    task3()
    # task4()
    # task4_check()
