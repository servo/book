# Building on WSL

Servo can be built on WSL as if you are building on any other Linux distribution.
To run non-headless servo shell on WSL, you will most likely need to be on Windows 10 Build 19044+ or Windows 11 as access to WSL v2 is needed for GUI.

1. Setup WSL v2.  See [Microsoft's guidelines for setting up GUI apps in WSL](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps).
2. Follow the [instructions](linux.md) for building and running Servo on the WSL distribution that you are using (e.g. Ubuntu, OpenSuse, etc.)

<div class="warning _note">

WSL v2 has the corresponding adaptors to display Wayland and X11 applications, though it may not always work out of the box with Servo.
</div>

### Troubleshooting

Be sure to look at the [General Troubleshooting](general-troubleshooting.md) section if you have trouble with your build and your problem is not listed below.

<pre><blockquote><samp>Failed to create event loop</samp></blockquote></pre>

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

# optionally save the variable long term to your .bashrc profile

echo 'export WAYLAND_DISPLAY=""' >> ~/.bashrc
```

<pre><blockquote><samp>Library libxkbcommon-x11.so could not be loaded</samp></blockquote></pre>

This may happen because your distro have not installed the required library. Run the following command (assuming you are using WSL Debian/Ubuntu, adjust accordingly if you use other distro):

```
sudo apt install libxkbcommon-x11-0
```

<pre><blockquote><samp>error: failed to run build command...</samp></blockquote></pre>

if you encounter an error like below while running `./mach build` on WSL, it is possibly caused by out of memory (OOM) error because your WSL does not have enough RAM to build servo.
You will need to increase memory usage limit and swapfile on WSL, or upgrade your RAM to fix it.
```shell
yourusername@PC:~/servo$ ./mach build
No build type specified so assuming `--dev`.
Building `debug` build with crown disabled (no JS garbage collection linting).
   ...
   Compiling script v0.0.1 (/home/yourusername/servo/components/script)

error: failed to run build command...

Caused by:
  process didn't exit successfully: `/home/yourusername/.rustup/toolchains/1.91.0-x86_64-unknown-linux-gnu/bin/rustc --crate-name script --edition=2024 components/script/lib.rs...
  ...
warning: build failed, waiting for other jobs to finish...
```

Create `C:/user/yourusername/.wslconfig` then insert the following:
```
[wsl2]
memory=6GB
swap=16GB
swapfile=C:\\Users\\yourusername\\swapfile.vhdx
```

Save the file and restart WSL on powershell:
```
wsl --shutdown
```
