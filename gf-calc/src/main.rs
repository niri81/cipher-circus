use clap::{Parser, Subcommand};
use std::{cmp::Ordering, num::TryFromIntError, process::exit};

#[derive(Parser)]
#[command(
    version,
    author = "aDR4MHI= <38499069+niri81@users.noreply.github.com>",
    about = "A simple Galois Field calculator in GF(2^8)",
    long_about = "A simple Galois Field calculator in GF(2^8). \
    Supported operations are Addition, Multiplication, Inversion and MixColumns with a predefined Matrix",
    help_template = "{about-section}\nBy:\t\t{author}\nVersion:\t{version} \n\n {usage-heading} {usage} \n {all-args} {tab}"
)]
#[command(propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    #[command(about = "Performs addition in GF(2^8)")]
    Add { num1: String, num2: String },
    #[command(about = "Performs multiplication in GF(2^8) with a given relation")]
    Mul {
        num1: String,
        num2: String,
        relation: String,
    },
    #[command(about = "Performs inversion in GF(2^8) with a given relation")]
    Inv { element: String, relation: String },
    #[command(
        about = "Performs an adaption of the MixColumns operation of AES in GF(2^8) with a predefined matrix and a given relation"
    )]
    MixCols { block: String, relation: String },
}

/// Allows for the definition of a GF(2^8) with its relation
pub struct GaloisField {
    relation: u16,
}

impl GaloisField {
    /// Performs multiplication in a given [GaloisField]
    fn multiply(&self, num1: &u8, num2: &u8) -> Result<u8, TryFromIntError> {
        // make computation more efficient by reducing the amount of shift operations
        let values = match num1.count_ones().cmp(&num2.count_ones()) {
            Ordering::Greater | Ordering::Equal => (u16::from(*num1), num2),
            Ordering::Less => (u16::from(*num2), num1),
        };

        log::debug!("values: {:#?}", values);
        let mut temp: u16 = 0;

        for i in (0..8).rev() {
            if (values.1 >> i) & 1 == 1 {
                log::debug!(
                    "bit {i} is set, proceeding with leftshift. num2 is: {:#b}",
                    num2
                );
                temp ^= values.0 << i;
                log::debug!(
                    "temp is now after leftshift and XOR with previous value: {:#b}",
                    temp
                );

                // if one of bits 8..15 is set
                while temp >> 8 > 0 {
                    log::debug!("need reducing");
                    // reduce num 1 by the relation shifted by the necessary amount of bits
                    log::debug!("temp before reducing: {:#b}", temp);
                    log::debug!(
                        "reducing with: {:#b}",
                        u32::from(self.relation) << (temp.ilog2() - 8)
                    );
                    temp ^= self.relation << (temp.ilog2() - 8);
                    log::debug!("temp after reducing: {:#b}", temp)
                }
            }
        }

        u8::try_from(temp)
    }

    /// Performs an adapted MixColumns operation (originally known from AES) in a given [GaloisField] with a predefined matrix
    fn mix_columns(&self, block: &[u8; 4]) -> [u8; 4] {
        let mut temp = *block;
        // same order as in AES
        const M: [u8; 4] = [0x59, 0x4f, 0x4c, 0x4f];

        for index in 0..block.len() / 2 {
            for j in 0..2 {
                // this is some formula I came up with after writing all operations out
                temp[2 * index + j] = addition(
                    &self.multiply(&block[2 * index], &M[j]).unwrap_or_else(|_| panic!("Error during multiplication of {:#04x}, {:#04x}. index: {index}, j: {j}",
                        block[2 * index],
                        M[j])),
                    &self
                        .multiply(&block[2 * index + 1], &M[j + 2])
                        .unwrap_or_else(|_| panic!("Error during multiplication of {:#04x}, {:#04x}. index: {index}, j: {j}",
                        block[2 * index + 1],
                        M[j + 2])),
                );
            }
        }

        temp
    }

    /// Determines the bruteforce in a given [GaloisField] via bruteforce
    fn bruteforce_inverse(&self, value: &u8) -> Option<u8> {
        (0..u8::MAX).find(|&i| self.multiply(value, &i) == Ok(1))
    }
}

/// Performs addition in GF(2^8)
pub fn addition(num1: &u8, num2: &u8) -> u8 {
    num1 ^ num2
}

/// A nice generic input parser
fn parse_input<T: num_traits::Num>(input: &str) -> T {
    match T::from_str_radix(input, 16) {
        Ok(val) => val,
        Err(_) => {
            log::error!("Error during conversion of {:#}", input);
            exit(-1);
        }
    }
}

fn main() {
    env_logger::init();
    let cli = Cli::parse();

    match &cli.command {
        Commands::Add { num1, num2 } => {
            println!(
                "Result after addition is: {:#04x}",
                addition(&parse_input(num1), &parse_input(num2))
            )
        }
        Commands::Mul {
            num1,
            num2,
            relation,
        } => {
            let gf = GaloisField {
                relation: parse_input(relation),
            };
            println!(
                "Result after multiplication is: {:#04x}",
                match gf.multiply(&parse_input(num1), &parse_input(num2)) {
                    Ok(val) => val,
                    Err(err) => {
                        log::error!("Error during multiplication: {}", err);
                        exit(-1);
                    }
                }
            )
        }
        Commands::MixCols { block, relation } => {
            let gf = GaloisField {
                relation: parse_input(relation),
            };

            let mut block = parse_input::<u32>(block).to_le_bytes();
            block.reverse();

            let block = gf.mix_columns(&block);
            println!("Result after mixColumns is: {:#?} or [", block);
            for i in block {
                println!("    {:02x},", i);
            }
            println!("]")
        }
        Commands::Inv { element, relation } => {
            let gf = GaloisField {
                relation: parse_input(relation),
            };

            let element = &parse_input(element);

            println!(
                "Inverse to {:#04x} is: {:#04x}",
                element,
                gf.bruteforce_inverse(element)
                    .unwrap_or_else(|| panic!("No inverse found for element {:#04x}", element))
            );
        }
    }
}
