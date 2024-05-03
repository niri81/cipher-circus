//! Implementation of the Schiffy-128 Feistel Cipher

fn main() {
    // exemplary use:
    // let sbox: [u32; 256] = generate_sbox();
    // let round_keys: [u128; 32] = ksa(&0xdeadbeef000000000000000badc0ffee);
    // feistel(&0x8a42d7b2eeb9add8, &round_keys[3], &sbox);

    /* println!(
        "Encryption Result {}",
        crypt(
            "0x00000000000000000000000000000000",
            &0x08150000000000000000000000004711,
            &Operation::Encrypt
        )
        .unwrap_or_else(|err| "An error occured: ".to_owned() + &err.to_string())
    ); */

    /* let ciphertext = "142af2b868801ac3fffccf9b882c15e7";
    let key = 0x08150000000000000000000000004711;

    println!(
        "Decryption Result: {}",
        crypt(ciphertext, &key, &Operation::Decrypt)
            .unwrap_or_else(|err| "An error occured: ".to_owned() + &err.to_string())
    ) */
}

/// Generation of the SBOX for Schiffy
fn generate_sbox() -> [u32; 256] {
    let mut sbox: [u32; 256] = [0; 256]; // unfortunately, a u32 type is necessary here due to the multiplication with 37 when generating the sboxes

    // set initial value, this makes computation in the for-loop easier and does not require an if-condition in the loop
    sbox[0] = 170;
    for i in 1..sbox.len() {
        sbox[i] = (37 * sbox[i - 1] + 9) % 256;
    }

    sbox
}

/// Implementation of the Key Scheduling Algorithm
fn ksa(key: &u128) -> [u128; 32] {
    let mut round_keys: [u128; 32] = [0; 32];

    // as K_0 is special and does not require a rotation, we can immediately set it and make computation in the for-loop easier again
    round_keys[0] = key ^ 0xabcdef;
    for i in 1..32 {
        round_keys[i] = round_keys[i - 1].rotate_left(7 * (i as u32)) ^ 0xabcdef;
    }
    round_keys
}

/// Internal function of the Feistel network
fn feistel(block: &u64, key: &u128, sbox: &[u32; 256]) -> u64 {
    // we need to cast these key-halves to u64s to ensure that they can be XORed with the block
    let key_msb: u64 = (key >> 64) as u64;
    let key_lsb: u64 = (key & 0xffff_ffff_ffff_ffff) as u64;

    let mut block: u64 = *block ^ key_msb;

    for i in 1..=8 {
        let mask: u64 = ((2 as u128).pow(8 * i) - (2 as u128).pow(8 * (i - 1))) as u64; // calculates 2^8i * 2^8(i-1) which serves as mask

        let block_value: usize = ((block & mask) >> 8 * (i - 1)) as usize; // as we want to use this value as an index for the sbox, we need to cast it to a usize
        let block_value: u64 = sbox[block_value] as u64; // now we shadow the block_value again with the sbox value

        // we shift the block value to the respective position in the block here
        // note: bitwise inversion is the ! operator in 🦀
        block = (block & !mask) | block_value << 8 * (i - 1)
    }

    // as the last step, the whole block is XORed with the last 64 bits of the key
    block ^ key_lsb
}

/// Enum that specifies the operation of the crypt function
/// 
/// This is a handy way of reusing the [crypt] method and executing the operation accordingly using matching
///
/// # Example
/// ```
/// crypt(ciphertext, &key, &Operation::Decrypt);
/// crypt(ciphertext, &key, &Operation::Encrypt);
/// ```
pub enum Operation {
    Encrypt,
    Decrypt,
}

/// Encryption and decryption function that handles user input
///
/// # Arguments
///
/// * `message` - Hex String that is to be encoded or decoded (should be multiple of 16 bytes/32 nibbles, else `\x00` will be added as padding within the string)
/// * `key` - Encryption/Decryption Key
/// * `operation` - [Operation] of the crypt function
///
/// # Example:
/// ```
/// let data: String = crypt("0x00000000000000000000000000000000", &0xdeadbeef000000000000000badc0ffee, &Operation::Encrypt);
///
/// assert_eq!(data, "b743f2fb342c51bfab950797083f61e9");
/// ```
pub fn crypt(
    message: &str,
    key: &u128,
    operation: &Operation,
) -> Result<String, std::num::ParseIntError> {
    let sbox: [u32; 256] = generate_sbox();
    let round_keys: [u128; 32] = ksa(&key);

    // we do not want messages starting with 0x, so we strip that prefix
    let message = if message.starts_with("0x") {
        message.strip_prefix("0x").unwrap()
    } else {
        message
    };

    let mut output: String = String::new();

    // split message in 32 char chunks (128 bit blocks, as we only want hex input)
    for block in message.chars().collect::<Vec<char>>().chunks(32) {
        // decode 128 bit block and match result (so that we can handle errors appropriately – `unwrap` is considered bad practice in 🦀 as it panics)
        let block: u128 = match u128::from_str_radix(&block.iter().collect::<String>(), 16) {
            Ok(val) => val,
            Err(err) => return Result::Err(err),
        };

        // break down blocks
        let mut left_block: u64 = (block >> 64) as u64;
        let mut right_block: u64 = (block & (u64::MAX) as u128) as u64;

        for i in 0..32 {
            // matching the executed operations
            match operation {
                Operation::Encrypt => {
                    let temp: u64 = right_block;
                    right_block = feistel(&right_block, &round_keys[i], &sbox) ^ left_block;
                    left_block = temp;
                }
                Operation::Decrypt => {
                    let temp: u64 = left_block;
                    left_block = feistel(&left_block, &round_keys[31 - i], &sbox) ^ right_block;
                    right_block = temp;
                }
            }
        }

        // appending the generated blocks to our output in hex format, this needs to be fixed length of 16 bytes (edge case of starting with 0, which is then cut off)
        output.push_str(&format!("{:016x}", left_block));
        output.push_str(&format!("{:016x}", right_block));
    }

    match operation {
        Operation::Encrypt => Result::Ok(output),
        // try to decode the result on decryption
        Operation::Decrypt => match hex::decode(&output) {
            Ok(val) => Result::Ok(String::from_utf8_lossy(&val).to_string()),
            Err(_) => Result::Ok(output),
        },
    }
}

/// The tests implemented with the given test vectors
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sbox_test_vectors() {
        let sbox: [u32; 256] = generate_sbox();

        assert_eq!(sbox[0], 170);
        assert_eq!(sbox[1], 155);
        assert_eq!(sbox[2], 112);
        assert_eq!(sbox[123], 33);
        assert_eq!(sbox[255], 205);
    }

    #[test]
    fn ksa_test_vectors() {
        let round_keys: [u128; 32] = ksa(&0xdeadbeef000000000000000badc0ffee);

        assert_eq!(round_keys[0], 0xdeadbeef000000000000000bad6b3201);
        assert_eq!(round_keys[1], 0x56df778000000000000005d6b532cd00);
        assert_eq!(round_keys[2], 0xdde00000000000000175ad4cb3ebd858);
        assert_eq!(round_keys[31], 0x770feb4b3180dc3bc09870bd38e2cb5f);
    }

    #[test]
    fn feistel_test_vectors() {
        let sbox: [u32; 256] = generate_sbox();
        let round_keys: [u128; 32] = ksa(&0xdeadbeef000000000000000badc0ffee);

        assert_eq!(
            feistel(&0x0000000000000000, &round_keys[0], &sbox),
            0x94dfb49607c198ab
        );
        assert_eq!(
            feistel(&0x94dfb49607c198ab, &round_keys[1], &sbox),
            0xb0aa7cca50e95fb1
        );
        assert_eq!(
            feistel(&0xb0aa7cca50e95fb1, &round_keys[2], &sbox),
            0x1e9d6324e9783573
        );
        assert_eq!(
            feistel(&0x8a42d7b2eeb9add8, &round_keys[3], &sbox),
            0x01a6283b0f33c8f0
        );
        assert_eq!(
            feistel(&0xc8ef99ba72f8a579, &round_keys[29], &sbox),
            0xf7ffea032144154a
        );
        assert_eq!(
            feistel(&0x81f3d4d01743d570, &round_keys[30], &sbox),
            0x7fac6b4146d4f4c6
        );
        assert_eq!(
            feistel(&0xb743f2fb342c51bf, &round_keys[31], &sbox),
            0x2a66d3471f7cb499
        );
    }

    #[test]
    fn encrypt_test_vector() {
        assert_eq!(
            crypt(
                "0x00000000000000000000000000000000",
                &0xdeadbeef000000000000000badc0ffee,
                &Operation::Encrypt
            )
            .unwrap(),
            "b743f2fb342c51bfab950797083f61e9"
        )
    }

    #[test]
    fn decrypt_test_vector() {
        assert_eq!(
            crypt(
                "2aed234f7ceda0ba9a89118bc0a0b93fe5b820aac165b97e3ad6338d23cb5858",
                &0x08150000000000000000000000004711,
                &Operation::Decrypt
            )
            .unwrap(),
            "--> https://tinyurl.com/4h6tbznj"
        );
    }
}
