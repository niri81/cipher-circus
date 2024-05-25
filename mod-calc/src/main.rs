use clap::{Parser, Subcommand};
use std::process::exit;

#[derive(Parser)]
#[command(
    version,
    author = "aDR4MHI= <38499069+niri81@users.noreply.github.com>",
    about = "A simple modulo calculator",
    long_about = "A simple modulo calculator. \
    Supported operations are Addition, Multiplication and Inversion",
    help_template = "{about-section}\nBy:\t\t{author}\nVersion:\t{version} \n\n {usage-heading} {usage} \n {all-args} {tab}"
)]
#[command(propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    #[command(about = "Performs addition")]
    Add {
        num1: i128,
        num2: i128,
        module: i128,
    },
    #[command(about = "Performs multiplication")]
    Mul {
        num1: i128,
        num2: i128,
        module: i128,
    },
    #[command(about = "Performs inversion")]
    Inv { element: i128, module: i128 },
    #[command(about = "Performs raising to the power")]
    Pow {
        element: i128,
        power: i128,
        module: i128,
    },
    #[command(about = "Performs reduction")]
    Red { element: i128, module: i128 },
}

pub struct FiniteField {
    module: u64,
}

impl FiniteField {
    fn reduce(&self, element: &u64) -> u64 {
        element % self.module
    }

    fn add(&self, num1: &u64, num2: &u64) -> u64 {
        (num1 + num2) % self.module
    }

    fn multiply(&self, num1: &u64, num2: &u64) -> u64 {
        (num1 * num2) % self.module
    }

    fn power(&self, num1: &u64, num2: &u32) -> u64 {
        (num1.pow(*num2)) % self.module
    }

    fn bruteforce_inverse(&self, element: &u64) -> Result<u64, String> {
        for i in 1..self.module {
            if (element * i) % self.module == 1 {
                return Ok(i);
            }
        }
        Err(format!("No inverse found for element {}", element))
    }

    fn normalize_input(&self, element: &i128) -> u64 {
        let mut element: i128 = *element;

        while element < 0 {
            element += i128::from(self.module);
        }

        match u64::try_from(element) {
            Ok(val) => val % self.module,
            Err(_) => {
                log::error!(
                    "Could not convert input {} to element after normalization",
                    element
                );
                exit(-1);
            }
        }
    }
}

fn init_field(module: &i128) -> FiniteField {
    FiniteField {
        module: match u64::try_from(*module) {
            Ok(val) => val,
            Err(_) => {
                log::error!(
                    "Could not convert input {} to element after normalization",
                    module
                );
                exit(-1);
            }
        },
    }
}

fn main() {
    env_logger::init();
    let cli = Cli::parse();

    match &cli.command {
        Commands::Add { num1, num2, module } => {
            let field = init_field(module);
            println!(
                "Result after addition is: {} mod {}",
                field.add(&field.normalize_input(num1), &field.normalize_input(num2)),
                field.module
            );
        }
        Commands::Mul { num1, num2, module } => {
            let field = init_field(module);

            println!(
                "Result after multiplication is: {} mod {}",
                field.multiply(&field.normalize_input(num1), &field.normalize_input(num2)),
                field.module
            );
        }
        Commands::Pow {
            element,
            power,
            module,
        } => {
            let field = init_field(module);

            println!(
                "Result after raising to the power is: {} mod {}",
                field.power(
                    &field.normalize_input(element),
                    &match u32::try_from(*power) {
                        Ok(val) => val,
                        Err(_) => {
                            log::error!(
                                "Could not convert input {} to element after normalization",
                                module
                            );
                            exit(-1);
                        }
                    }
                ),
                field.module
            );
        }
        Commands::Inv { element, module } => {
            let field = init_field(module);

            match field.bruteforce_inverse(&field.normalize_input(element)) {
                Ok(val) => println!("Result after inversion is: {} mod {}", val, field.module),
                Err(err) => println!("{}", err),
            }
        }
        Commands::Red { element, module } => {
            let field = init_field(module);
            println!(
                "Result after reduction is: {} mod {}",
                field.reduce(&field.normalize_input(element)),
                field.module
            );
        }
    }
}
