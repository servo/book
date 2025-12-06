# Crate Dependencies

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

# Working on a crate

As explained above, Servo depends on a lot of libraries, which makes it very modular.
While working on a bug in Servo, you'll often end up in one of its dependencies.
You will then want to compile your own version of the dependency (and maybe compiling against the HEAD of the library will fix the issue!).

For example, I'm trying to bring some cocoa events to Servo.
The Servo window on Desktop is constructed with a library named [winit](https://github.com/rust-windowing/winit).
winit itself depends on a cocoa library named [cocoa-rs](https://github.com/servo/cocoa-rs).
When building Servo, magically, all these dependencies are downloaded and built for you.
But because I want to work on this cocoa event feature, I want Servo to use my own version of _winit_ and _cocoa-rs_.

This is how my projects are laid out:

```
~/my-projects/servo/
~/my-projects/cocoa-rs/
```

Both folders are git repositories.

To make it so that servo uses `~/my-projects/cocoa-rs/`, first ascertain which version of the crate Servo is using and whether it is a git dependency or one from crates.io.

Both information can be found using, in this example, `cargo pkgid cocoa`(`cocoa` is the name of the package, which doesn't necessarily match the repo folder name).

If the output is in the format `https://github.com/servo/cocoa-rs#cocoa:0.0.0`, you are dealing with a git dependency and you will have to edit the `~/my-projects/servo/Cargo.toml` file and add at the bottom:

```toml
[patch]
"https://github.com/servo/cocoa-rs#cocoa:0.0.0" = { path = '../cocoa-rs' }
```

If the output is in the format `https://github.com/rust-lang/crates.io-index#cocoa#0.0.0`, you are dealing with a crates.io dependency and you will have to edit the `~/my-projects/servo/Cargo.toml` in the following way:

```toml
[patch]
"cocoa:0.0.0" = { path = '../cocoa-rs' }
```

Both will tell any cargo project to not use the online version of the dependency, but your local clone.

For more details about overriding dependencies, see [Cargo's documentation](https://doc.crates.io/specifying-dependencies.html#overriding-dependencies).

# Requesting crate releases

In addition to creating the Servo browser engine, the Servo project also publishes modular components when they can benefit the wider community of Rust developers.
An example of one of these crates is [`rust-url`](https://crates.io/crates/url).
While we strive to be good maintainers, managing the process of building a browser engine and a collection of external libraries can be a lot of work, thus we make no guarantees about regular releases for these modular crates.

If you feel that a release for one of these crates is due, we will respond to requests for new releases.
The process for requesting a new release is:

1. Create one or more pull requests that prepare the crate for the new release.
2. Create a pull request that increases the version number in the repository, being careful to keep track of what component of the version should increase since the last release. This means that you may need to note if there are any breaking changes.
3. In the pull request ask that a new version be released. The person landing the change has the responsibility to publish the new version or explain why it cannot be published with the landing of the pull request.
