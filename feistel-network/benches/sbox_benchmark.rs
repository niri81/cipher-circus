//! As I was interested in the time needed to generate the sboxes, I created a benchmark for this.
//! Run with `cargo bench`

use criterion::{criterion_group, criterion_main, Criterion};

fn generate_sbox() -> [u32; 256] {
    let mut sbox: [u32; 256] = [0; 256]; // unfortunately, a u32 type is necessary here due to the multiplication with 37 when generating the sboxes

    sbox[0] = 170;
    for i in 1..sbox.len() {
        sbox[i] = (37 * sbox[i - 1] + 9) % 256;
    }

    sbox
}

fn criterion_benchmark(c: &mut Criterion) {
    c.bench_function("sbox generator", |b| b.iter(|| generate_sbox()));
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
