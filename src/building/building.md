# Building Servo

This page contains more detailed information about building Servo.
You might want to skip straight to instructions for building Servo on your system:

- [Linux](linux.md)
- [macOS](macos.md)
- [Windows](windows.md)
- [NixOS](nixos.md)
- [WSL](wsl.md)
- [Android](android.md)
- [OpenHarmony](openharmony.md)

# mach

You need to use `mach` to build Servo.
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

## Build profiles

There are three main build profiles, which you can build and use independently of one another:

- debug builds, which allow you to use a debugger (lldb) (selected by default if no profile is passed)
- release builds, which are slower to build but more performant
- production builds, which are used for official releases only

<table>
<thead>
    <tr>
        <th></th>
        <th>debug</th>
        <th>release</th>
        <th>production</th>
    </tr>
</thead>
<tbody>
    <tr>
        <th>mach option</th>
        <td><code>-d<br>--debug</code></td>
        <td><code>-r<br>--release</code></td>
        <td><code>--prod<br>--production</code></td>
    </tr>
    <tr>
        <th>optimised?</th>
        <td><a href="https://doc.rust-lang.org/cargo/reference/profiles.html#dev">no</a></td>
        <td><a href="https://github.com/servo/servo/blob/457d37d94ee6966cad377c373d333a00c637e1ae/Cargo.toml#L153">yes</a></td>
        <td>yes, <a href="https://github.com/servo/servo/blob/9457a40ca2cd4b9530ba7c5334c82f3b3f2e7ac8/Cargo.toml#L177-L182">more than</a> in <strong>release</strong></td>
    </tr>
    <tr>
        <th>maximum RUST_LOG level</th>
        <td><code>trace</code></td>
        <td><code>info</code></td>
        <td><code>info</code></td>
    </tr>
    <tr>
        <th>debug assertions?</th>
        <td>yes</td><td>yes(!)</td><td>no</td>
    </tr>
    <tr>
        <th>debug info?</th>
        <td>yes</td><td>no</td><td>no</td>
    </tr>
    <tr>
        <th>symbols?</th>
        <td>yes</td><td>no</td><td>yes</td>
    </tr>
    <tr>
        <th>finds resources in<br>current working dir?</th>
        <td>yes</td><td>yes</td><td>no(!)</td>
    </tr>
</tbody>
</table>

There are also two special variants of production builds for performance-related use cases:

- `production-stripped` builds are ideal for benchmarking Servo over time, with debug symbols stripped for faster initial startup
- `profiling` builds are ideal for [profiling](../contributing/profiling.md) and troubleshooting performance issues; they behave like a debug or release build, but have the same performance as a production build

<table>
<thead>
    <tr>
        <th></th>
        <th>production</th>
        <th>production-stripped</th>
        <th>profiling</th>
    </tr>
</thead>
<tbody>
    <tr>
        <th>mach <code>--profile</code></th>
        <td><code>production</code></td>
        <td><code>production-stripped</code></td>
        <td><code>profiling</code></td>
    </tr>
    <tr>
        <th>debug info?</th>
        <td>no</td><td>no</td><td>yes</td>
    </tr>
    <tr>
        <th>symbols?</th>
        <td>yes</td><td>no</td><td>yes</td>
    </tr>
    <tr>
        <th>finds resources in<br>current working dir?</th>
        <td>no</td><td>no</td><td>yes(!)</td>
    </tr>
</tbody>
</table>

You can change these settings in a servobuild file (see [servobuild.example](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/servobuild.example)) or in the root [Cargo.toml](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/Cargo.toml).

## Optional build settings

Some build settings can only be enabled manually:

- **AddressSanitizer builds** are enabled with `./mach build --with-asan`
- **ThreadSanitizer builds** are enabled with `./mach build --with-tsan`
- **crown linting** is recommended when hacking on DOM code, and is enabled with `./mach build --use-crown`
- **SpiderMonkey debug builds** are enabled with `./mach build --debug-mozjs`, or `[build] debug-mozjs = true` in your servobuild file

A full list of arguments can be seen by running `./mach build --help`.

## Running servoshell

When you build it yourself, servoshell will be in `target/debug/servo` or `target/release/servo`.
You can run it directly as shown above, but we recommend using [mach](#mach) instead.

To run servoshell with mach, replace `./servo` with `./mach run -d --` or `./mach run -r --`, depending on the [build profile](#build-profiles) you want to run.
For example, both of the commands below run the debug build of servoshell with the same options:

```sh
$ target/debug/servo https://demo.servo.org
$ ./mach run -d -- https://demo.servo.org
```
