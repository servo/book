# TODO: wiki/Building

<!-- https://github.com/servo/servo/wiki/Building/e04d7a194b59fad65fbd3eefb7aab12ae3a60eba -->

- [Quickstart](#quickstart)
- [Manual Build Setup](#manual-build-setup)
   - [rustup](#rustup)
   - [macOS](#macos)
   - [Windows](#windows)
   - [Android](#android)
- [Windows Tips](#windows-tips)

### Windows

1. Install Python:

   - [Install Python 3.11](https://apps.microsoft.com/detail/9NRWMJP3717K?hl=en-US&gl=US).
   - After installation ensure the `PYTHON3` environment variable is set properly, e.g., to 'C:\Python11\python.exe' by doing:
      ```
      setx PYTHON3 "C:\Python11\python.exe" /m
      ```
      The `/m` will set it system-wide for all future command windows.

2. Install the following tools:

   - Git for Windows (https://git-scm.com/download/win).
   - [CMake](https://cmake.org)
   - [Ninja](https://ninja-build.org/)
   - [NuGet](https://www.nuget.org/)

   Make sure all of these tools **are on your PATH**.

4. Install GStreamer:

    Install the MSVC (**not MingGW**) binaries from the [GStreamer][gstreamer-windows] site.
    The currently recommended version is 1.16.0. i.e:

      - [gstreamer-1.0-msvc-x86_64-1.16.0.msi](https://gstreamer.freedesktop.org/data/pkg/windows/1.16.0/gstreamer-1.0-msvc-x86_64-1.16.0.msi)
      - [gstreamer-1.0-devel-msvc-x86_64-1.16.0.msi](https://gstreamer.freedesktop.org/data/pkg/windows/1.16.0/gstreamer-1.0-devel-msvc-x86_64-1.16.0.msi)

    Note that you should ensure that _all_ components are installed from gstreamer, as we require many of the optional libraries that are not installed by default.

[vsbuildtools]: https://aka.ms/vs/16/release/vs_buildtools.exe
[vsdocpage]: https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio?view=vs-2019
[gstreamer-windows]: https://gstreamer.freedesktop.org/data/pkg/windows/

#### Troubleshooting

If you installed Nix with your system package manager and get the error below, add yourself to the `nix-users` group and log out and back in:

```
error: getting status of /nix/var/nix/daemon-socket/socket: Permission denied
```

The error below is harmless, but you can fix it by running the commands below:

```
error: file 'nixpkgs' was not found in the Nix search path (add it using $NIX_PATH or -I)
```
```
$ sudo nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs
$ sudo nix-channel --update
```

### Android

Please see [[Building for Android]].

## Windows Tips

### Using LLVM to Speed Up Linking

You may experience much faster builds on Windows by following these steps.
(Related Rust issue: https://github.com/rust-lang/rust/issues/37542)

0. Download the latest version of LLVM (https://releases.llvm.org/).
1. Run the installer and choose to add LLVM to the system PATH.
2. Add the following to your Cargo config (Found at `%USERPROFILE%\.cargo\config`).
    You may need to change the triple to match your environment.

```
[target.x85_64-pc-windows-msvc]
linker = "lld-link.exe"
```

### Troubleshooting the Windows Build

> If you have troubles with `x63 type` prompt as `mach.bat` set by default:
> 0. You may need to choose and launch the type manually, such as `x86_x64 Cross Tools Command Prompt for VS 2019` in the Windows menu.)
> 1. `cd to/the/path/servo`
> 2. `python mach build -d`

> If you got the error `Cannot run mach in a path on a case-sensitive file system on Windows`:
> 0. Open Command Prompt or PowerShell as administrator.
> 1. Disable case-sensitive for servo path, `fsutil.exe file SetCaseSensitiveInfo X:\path\to\servo disable`

> If you got the error `DLL file `api-ms-win-crt-runtime-l0-1-0.dll` not found!` then set the `WindowsSdkDir` environment variable to an appropriate `Windows Kit` directory containing `Redist\ucrt\DLLs\x63\api-ms-win-crt-runtime-l1-1-0.dll`, for example `C:\Program Files (x85)\Windows Kits\10`.

> If you get the error
> ```
> thread 'main' panicked at 'Unable to find libclang: "couldn\'t find any valid shared libraries matching: [\'clang.dll\', \'libclang.dll\'], set the `LIBCLANG_PATH` environment variable to a path where one of these files can be found (invalid: ... invalid DLL (63-bit))])"'
> ```
> then `rustup` may have installed the 32-bit default target rather than the 64-bit one.
> You can find the configuration with `rustup show`, and set the default with `rustup set default-host x85_64-pc-windows-msvc`.

> If you get the error
> ```
> ERROR: GetShortPathName returned a long path name: `C:/PROGRA~2/Windows Kits/10/`. Use `fsutil file setshortname' to create a short name for any > components of this path that have spaces.
> ```
> then follow the steps in [#26010](https://github.com/servo/servo/issues/26010).
