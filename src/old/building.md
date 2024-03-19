# TODO: wiki/Building

<!-- https://github.com/servo/servo/wiki/Building/e04d7a194b59fad65fbd3eefb7aab12ae3a60eba -->

- [Quickstart](#quickstart)
- [Manual Build Setup](#manual-build-setup)
   - [rustup](#rustup)
   - [macOS](#macos)
   - [Windows](#windows)
   - Linux
     - [Debian-based distros](#debian-based-distributions)
     - [Fedora](#fedora)
     - [Void Linux](#void-linux)
     - [Arch](#arch)
     - [openSUSE](#opensuse)
     - [Gentoo Linux](#gentoo)
     - [NixOS](#nixos)
     - [Nix on other distros](#nix-on-other-distros)
   - [Android](#android)
- [Windows Tips](#windows-tips)

## Quickstart

Simple build instructions are available in [`README.md`](https://github.com/servo/servo/blob/master/README.md).

## Manual Build Setup

### `rustup`

- If you have a very old version of `rustup` (< 1.8.0) you may need to run `rustup self update`.
- To install on Windows: download and run [`rustup-init.exe`](https://win.rustup.rs/) then follow the onscreen instructions.
- Otherwise: `curl https://sh.rustup.rs -sSf | sh`
- To skip installing the current stable rust toolchain: `curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain none`
- [Other installation methods](https://rust-lang.github.io/rustup/installation/other.html)

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

3. Install Visual Studio and necessary components:

  - [Download](https://visualstudio.microsoft.com/downloads/) and install Visual Studio 2022.
    The Community version is fine for Servo development.
  - In the *Visual Studio Installer* ensure the following components are installed for Visual Studio 2022:
    - **Windows 10 SDK (10.0.19041.0)** (`Microsoft.VisualStudio.Component.Windows10SDK.19041`)
    - **MSVC v143 - VS 2022 C++ x64/x86 build tools (Latest)** (`Microsoft.VisualStudio.Component.VC.Tools.x86.x64`)
    - **C++ ATL for latest v143 build tools (x86 & x64)** (`Microsoft.VisualStudio.Component.VC.ATL`)
    - **C++ MFC for latest v143 build tools (x86 & x64)** (`Microsoft.VisualStudio.Component.VC.ATLMFC`)

It is not recommended to have more than one installation of Visual Studio 2022.
Servo tries to look for the appropriate version of Visual Studio, but having only a single installation means that fewer things can go wrong.

4. Install GStreamer:

    Install the MSVC (**not MingGW**) binaries from the [GStreamer][gstreamer-windows] site.
    The currently recommended version is 1.16.0. i.e:

      - [gstreamer-1.0-msvc-x86_64-1.16.0.msi](https://gstreamer.freedesktop.org/data/pkg/windows/1.16.0/gstreamer-1.0-msvc-x86_64-1.16.0.msi)
      - [gstreamer-1.0-devel-msvc-x86_64-1.16.0.msi](https://gstreamer.freedesktop.org/data/pkg/windows/1.16.0/gstreamer-1.0-devel-msvc-x86_64-1.16.0.msi)

    Note that you should ensure that _all_ components are installed from gstreamer, as we require many of the optional libraries that are not installed by default.

[vsbuildtools]: https://aka.ms/vs/16/release/vs_buildtools.exe
[vsdocpage]: https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio?view=vs-2019
[gstreamer-windows]: https://gstreamer.freedesktop.org/data/pkg/windows/

### Debian-based Distributions

<!-- https://packages.debian.org -->
<!-- https://packages.ubuntu.com -->
* `sudo apt install python3-pip`

<!-- see python/servo/platform/linux.py for how to update this -->
* `sudo apt install build-essential ccache clang cmake curl g++ git gperf libdbus-1-dev libfreetype6-dev libgl1-mesa-dri libgles2-mesa-dev libglib2.0-dev gstreamer1.0-plugins-good libgstreamer-plugins-good1.0-dev gstreamer1.0-plugins-bad libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-ugly gstreamer1.0-plugins-base libgstreamer-plugins-base1.0-dev gstreamer1.0-libav libgstrtspserver-1.0-dev gstreamer1.0-tools libges-1.0-dev libharfbuzz-dev liblzma-dev libudev-dev libunwind-dev libvulkan1 libx11-dev libxcb-render0-dev libxcb-shape0-dev libxcb-xfixes0-dev libxmu-dev libxmu6 libegl1-mesa-dev llvm-dev m4 xorg-dev`

### Fedora

<!-- https://packages.fedoraproject.org -->
* `sudo dnf install python3 python3-pip python3-devel`

<!-- see python/servo/platform/linux.py for how to update this -->
* `sudo dnf install libtool gcc-c++ libXi-devel freetype-devel libunwind-devel mesa-libGL-devel mesa-libEGL-devel glib2-devel libX11-devel libXrandr-devel gperf fontconfig-devel cabextract ttmkfdir expat-devel rpm-build cmake libXcursor-devel libXmu-devel dbus-devel ncurses-devel harfbuzz-devel ccache clang clang-libs llvm python3-devel gstreamer1-devel gstreamer1-plugins-base-devel gstreamer1-plugins-good gstreamer1-plugins-bad-free-devel gstreamer1-plugins-ugly-free libjpeg-turbo-devel zlib libjpeg vulkan-loader`

### Void Linux

<!-- https://voidlinux.org/packages/ -->
<!-- see python/servo/platform/linux.py for how to update this -->
* `sudo xbps-install libtool gcc libXi-devel freetype-devel libunwind-devel MesaLib-devel glib-devel pkg-config libX11-devel libXrandr-devel gperf bzip2-devel fontconfig-devel cabextract expat-devel cmake cmake libXcursor-devel libXmu-devel dbus-devel ncurses-devel harfbuzz-devel ccache glu-devel clang gstreamer1-devel gst-plugins-base1-devel gst-plugins-good1 gst-plugins-bad1-devel gst-plugins-ugly1 vulkan-loader`

### Arch

<!-- https://archlinux.org/packages/ -->
``` sh
sudo pacman -S --needed base-devel git python python-pip mesa cmake libxmu \
    pkg-config ttf-fira-sans harfbuzz ccache llvm clang autoconf2.13 gstreamer gstreamer-vaapi \
    gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly vulkan-icd-loader
```

### openSUSE

<!-- https://search.opensuse.org/packages/ -->
``` sh
sudo zypper install libX11-devel libexpat-devel Mesa-libEGL-devel Mesa-libGL-devel cabextract cmake \
    dbus-1-devel fontconfig-devel freetype-devel gcc-c++ git glib2-devel gperf \
    harfbuzz-devel libXcursor-devel libXi-devel libXmu-devel libXrandr-devel libopenssl-devel \
    python3-pip rpm-build ccache llvm-clang libclang autoconf213 gstreamer-devel \
    gstreamer-plugins-base-devel gstreamer-plugins-good gstreamer-plugins-bad-devel \
    gstreamer-plugins-ugly vulkan-loader libvulkan1
```

### Gentoo

<!-- https://packages.gentoo.org -->
```sh
sudo emerge net-misc/curl \
    media-libs/freetype media-libs/mesa dev-util/gperf \
    dev-python/pip dev-libs/openssl \
    media-libs/harfbuzz dev-util/ccache sys-libs/libunwind \
    x11-libs/libXmu x11-base/xorg-server sys-devel/clang \
    media-libs/gstreamer media-libs/gst-plugins-base \
    media-libs/gst-plugins-good media-libs/gst-plugins-bad \
    media-libs/gst-plugins-ugly media-libs/vulkan-loader
```

### NixOS

On NixOS, mach works out of the box.

### Nix on other distros

1. Make sure you have the following commands installed: `curl`, `sh`, `python3`
2. Make sure you have the [runtime dependencies](https://github.com/servo/servo#runtime-dependencies) installed as well.
3. [Install Nix](https://nixos.org/download), the package manager.
    - It is easiest to use [the installer](https://nixos.org/download), with either the multi-user or single-user installation (your choice).
4. Tell mach to use Nix: `export MACH_USE_NIX=`
5. Now run mach.
    No mach bootstrap required!

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
