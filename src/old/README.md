# TODO: README.md

<!-- https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/README.md -->

# The Servo Parallel Browser Engine Project

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`HACKING_QUICKSTART.md`](docs/HACKING_QUICKSTART.md) for help getting started.

## Build Setup

* [macOS](#macos)
* [Linux](#Linux)
* [Windows](#windows)
* [Android](https://github.com/servo/servo/wiki/Building-for-Android)

If these instructions fail or you would like to install dependencies manually, try the [manual build setup][manual-build].

### macOS

- Run `./mach bootstrap`<br/>
  *Note: This will install the recommended version of GStreamer globally on your system.*

### Windows

- Run `mach bootstrap`
  - *This will install CMake, Git, and Ninja via choco in an Administrator console.
    Allow the scripts to run and once the operation finishes, close the new console.*
- Run `refreshenv`

See also [Windows Troubleshooting Tips][windows-tips].

### Android

- Ensure that the following environment variables are set:
  - `ANDROID_SDK_ROOT`
  - `ANDROID_NDK_ROOT`: `$ANDROID_SDK_ROOT/ndk/25.2.9519653/`<br>
    `ANDROID_SDK_ROOT` can be any directory (such as `~/android-sdk`).
    All of the Android build dependencies will be installed there.
- Install the latest version of the [Android command-line tools](https://developer.android.com/studio#command-tools) to `$ANDROID_SDK_ROOT/cmdline-tools/latest`.
- Run the following command to install the necessary components:
  ```shell
  sudo $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --install
   "build-tools;33.0.2" \
   "emulator" \
   "ndk;25.2.9519653" \
   "platform-tools" \
   "platforms;android-33" \
   "system-images;android-33;google_apis;x86_64"
  ```
For information about building and running the Android build, see the [Android documentation][android-docs].

### The Rust compiler

Servo's build system uses rustup.rs to automatically download a Rust compiler.
This is a specific version of Rust Nightly determined by the [`rust-toolchain.toml`](https://github.com/servo/servo/blob/main/rust-toolchain.toml) file.

### Checking for build errors, without building

If you’re making changes to one crate that cause build errors in another crate, consider this instead of a full build:

```sh
./mach check
```

It will run `cargo check`, which runs the analysis phase of the compiler (and so shows build errors if any) but skips the code generation phase.
This can be a lot faster than a full build, though of course it doesn’t produce a binary you can run.

### Commandline Arguments

- `-p INTERVAL` turns on the profiler and dumps info to the console every `INTERVAL` seconds
- `-s SIZE` sets the tile size for painting; defaults to 512
- `-z` disables all graphical output; useful for running JS / layout tests
- `-Z help` displays useful output to debug servo

### Keyboard Shortcuts

- `Ctrl`+`L` opens URL prompt (`Cmd`+`L` on Mac)
- `Ctrl`+`R` reloads current page (`Cmd`+`R` on Mac)
- `Ctrl`+`-` zooms out (`Cmd`+`-` on Mac)
- `Ctrl`+`=` zooms in (`Cmd`+`=` on Mac)
- `Alt`+`left arrow` goes backwards in the history (`Cmd`+`left arrow` on Mac)
- `Alt`+`right arrow` goes forwards in the history (`Cmd`+`right arrow` on Mac)
- `Esc` or `Ctrl`+`Q` exits Servo (`Cmd`+`Q` on Mac)

## Developing

The generated documentation can be found on https://doc.servo.org/servo/index.html

[manual-build]: https://github.com/servo/servo/wiki/Building#manual-build-setup
[windows-tips]: https://github.com/servo/servo/wiki/Building#troubleshooting-the-windows-build
[android-docs]: https://github.com/servo/servo/wiki/Building-for-Android
