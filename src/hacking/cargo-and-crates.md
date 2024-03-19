<!-- TODO: needs copyediting -->

# Cargo and crates

A Rust library is called a crate.
Servo uses plenty of crates.
These crates are dependencies.
They are listed in files called `Cargo.toml`.
Servo is split into components and ports (see `components` and `ports` directories).
Each has its own dependencies, and each has its own `Cargo.toml` file.

`Cargo.toml` files list the dependencies.
You can edit this file.

For example, `components/net_traits/Cargo.toml` includes:

```
 [dependencies.stb_image]
 git = "https://github.com/servo/rust-stb-image"
```

But because `rust-stb-image` API might change over time, it's not safe to compile against the `HEAD` of `rust-stb-image`.
A `Cargo.lock` file is a snapshot of a `Cargo.toml` file which includes a reference to an exact revision, ensuring everybody is always compiling with the same configuration:

```
[[package]]
name = "stb_image"
source = "git+https://github.com/servo/rust-stb-image#f4c5380cd586bfe16326e05e2518aa044397894b"
```

This file should not be edited by hand.
In a normal Rust project, to update the git revision, you would use `cargo update -p stb_image`, but in Servo, use `./mach cargo-update -p stb_image`.
Other arguments to cargo are also understood, e.g. use --precise '0.2.3' to update that crate to version 0.2.3.

See [Cargo's documentation about Cargo.toml and Cargo.lock files](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html).
