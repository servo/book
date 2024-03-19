<!-- TODO: needs copyediting -->

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

Both folder are git repositories.

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
