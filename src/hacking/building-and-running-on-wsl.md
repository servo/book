# Building and Running on WSL

To run non-headless servo shell on WSL, you will most likely need to be on Windows 10 Build 19044+ or Windows 11 as access to WSL v2 is needed for GUI.

## Building

Servo can be built on WSL as if you are building on any other Linux distribution.

1. Setup WSL v2.  See [Microsoft's guidelines for setting up GUI apps in WSL](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps).
2. Set up the environment depending on the WSL distribution that you are using (e.g. Ubuntu, OpenSuse, etc.)
3. Build

## Running

WSL v2 has the corresponding adaptors to display Wayland and X11 applications, though it may not always work out of the box with Servo.

### Troubleshooting

**Failed to create event loop**:

If you encounter an immediate crash after running that points to winit and its platform implementation, setting `WAYLAND_DISPLAY=''` stops the crash.

```
Failed to create events loop: Os(OsError { line: 81, file: "/home/astra/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/winit-0.30.9/src/platform_impl/linux/wayland/event_loop/mod.rs", error: WaylandError(Connection(NoCompositor)) }) (thread main, at ports/servoshell/desktop/cli.rs:34)
   0: servoshell::backtrace::print
             at /home/astra/workspace/servo/ports/servoshell/backtrace.rs:18:5
  ...
  18: main
  19: <unknown>
  20: __libc_start_main
  21: _start
Servo was terminated by signal 11
```

Either export the variable, or set it before running:
```shell
export WAYLAND_DISPLAY=''
./mach run

# or

WAYLAND_DISPLAY='' ./mach run
```
