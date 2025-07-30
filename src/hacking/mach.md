# mach

`mach` is a Python program that does plenty of things to make working on Servo easier, like building and running Servo, running tests, and updating dependencies.

**Windows users:** you will need to replace `./mach` with `.\mach` in the commands in this book if you are using cmd.

Use `--help` to list the subcommands, or get help with a specific subcommand:

```sh
$ ./mach --help
$ ./mach build --help
```

When you use mach to run another program, such as servoshell, that program may have its own options with the same names as mach options.
You can use `--`, surrounded by spaces, to tell mach not to touch any subsequent options and leave them for the other program.

```sh
$ ./mach run --help         # Gets help for `mach run`.
$ ./mach run -d --help      # Still gets help for `mach run`.
$ ./mach run -d -- --help   # Gets help for the debug build of servoshell.
```

This also applies to the Servo unit tests, where there are three layers of options: mach options, `cargo test` options, and [libtest options](https://doc.rust-lang.org/cargo/commands/cargo-test.html#description).

```sh
$ ./mach test-unit --help           # Gets help for `mach test-unit`.
$ ./mach test-unit -- --help        # Gets help for `cargo test`.
$ ./mach test-unit -- -- --help     # Gets help for the test harness (libtest).
```

Work is ongoing to make it possible to build Servo without mach.
Where possible, consider whether you can use native Cargo functionality before adding new functionality to mach.
