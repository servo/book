# Setting up your environment

Before you can build Servo, you will need to:

1. [**Check**](#check-tools) if you have the necessary tools.
  If not, install them: [**Windows**](#tools-for-windows), [**macOS**](#tools-for-macos), [**Linux**](#tools-for-linux)
2. [**Check**](#check-tools) your tools again.
  If not, you may need to restart your shell, or log out and log back in.
3. If you are on **NixOS**, you can stop here, no further action needed!
4. Install the other dependencies by running `./mach bootstrap` (or `.\mach bootstrap` on **Windows**).
  If you prefer not to do that, or your **Linux** distro is unsupported by mach, you can instead follow the steps below:
    - Try the [Nix method](#nix-method) or a distro-specific method: [Arch](#dependencies-for-arch), [Debian](#dependencies-for-debian), [elementary OS](#dependencies-for-debian), [Fedora](#dependencies-for-fedora), [Gentoo](#dependencies-for-gentoo), [KDE neon](#dependencies-for-debian), [Linux Mint](#dependencies-for-debian), [Manjaro](#dependencies-for-arch), [openSUSE](#dependencies-for-opensuse), [Pop!_OS](#dependencies-for-debian), [Raspbian](#dependencies-for-debian), [TUXEDO OS](#dependencies-for-debian), [Ubuntu](#dependencies-for-debian), [Void Linux](#dependencies-for-void-linux)
    - Install `taplo` and `crown` by running `./mach bootstrap --skip-platform`

<div class="warning _note">

**Sometimes the tools or dependencies needed to build Servo will change.**
If you start encountering build problems after updating Servo, try running `./mach bootstrap` again, or [set up your environment](setting-up-your-environment.md) from the beginning.

**You are not alone!**
If you have problems setting up your environment that you can’t solve, you can always ask for help in the [build issues](https://servo.zulipchat.com/#narrow/stream/263398-general/topic/Build.20Issues) chat on Zulip.
</div>

## Checking if you have the tools installed { #check-tools }

- `curl --version` should print a version like 7.83.1 or 8.4.0
  - On Windows, type `curl.exe --version` instead, to avoid getting the PowerShell alias for `Invoke-WebRequest`
- `uv --version` should print **0.4.30 or newer**
  - Servo's `mach` build tool depends on `uv` to provision a pinned version of Python (set by the `.python-version` file in the repo) and create a local virtual environment (`.venv` directory) into which the python dependency modules are installed.
  - If the system already has an installation of the required Python version, then `uv` will just symlink to that installation to save disk space.
  - If the versions do not match or no Python installation is present on the host, then `uv` will download the required binaries.
  - Using an externally managed Python installation for executing `mach` as a Python script is currently not supported.
- `rustup --version` should print a version like 1.26.0
- (Windows only) `choco --version` should print a version like 2.2.2
- (macOS only) `brew --version` should print a version like 4.2.17

## Tools for Windows

Note that `curl` will already be installed on Windows 1804 or newer.

- Download and install `uv` [from the uv website](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
- Download and install `choco` [from the Chocolatey website](https://chocolatey.org/install#individual)
- **If you already have `rustup`,** download the [Build Tools for Visual Studio 2022](https://aka.ms/vs/17/release/vs_BuildTools.exe)
- **If you don’t have `rustup`,** download and run the `rustup` installer: [`rustup-init.exe`](https://win.rustup.rs/)
  - Be sure to select *Quick install via the Visual Studio Community installer*
- In the Visual Studio installer, ensure the following components are installed:
  - **Windows 10 SDK (anything >= 10.0.19041.0)**<br>
    (`Microsoft.VisualStudio.Component.Windows10SDK.{>=19041}`)
  - **MSVC v143 - VS 2022 C++ x64/x86 build tools (Latest)**<br>
    (`Microsoft.VisualStudio.Component.VC.Tools.x86.x64`)
  - **C++ ATL for latest v143 build tools (x86 & x64)**<br>
    (`Microsoft.VisualStudio.Component.VC.ATL`)
  - **C++ MFC for latest v143 build tools (x86 & x64)**<br>
    (`Microsoft.VisualStudio.Component.VC.ATLMFC`)

<div class="warning _note">

**We don’t recommend having more than one version of Visual Studio installed.**
Servo will try to search for the appropriate version of Visual Studio, but having only a single version installed means fewer things can go wrong.
</div>

## Tools for macOS

Note that `curl` will already be installed on macOS.

- Download and install `uv` [from the uv website](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
- Download and install [Xcode](https://developer.apple.com/xcode/)
- Download and install `brew` [from the Homebrew website](https://brew.sh/)
- Download and install `rustup` [from the rustup website](https://rustup.rs/)

## Tools for Linux

- Install `curl`:
  - Arch: `sudo pacman -S --needed curl`
  - Debian, Ubuntu: `sudo apt install curl`
  - Fedora: `sudo dnf install curl`
  - Gentoo: `sudo emerge net-misc/curl`
- Download and install `uv` [from the uv website](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
- Download and install `rustup` [from the rustup website](https://rustup.rs/)

On **NixOS**, type `nix-shell` to enter a shell with all of the necessary tools and dependencies.

## Dependencies for any Linux distro, using Nix { #nix-method }

- Make sure you have `curl` installed (see [*Tools for Linux*](#tools-for-linux))
- Make sure you have the [runtime dependencies](../running-servoshell.md#runtime-dependencies) installed as well
- [Install Nix](https://nixos.org/download), the package manager — the easiest way is to use the installer, with either the multi-user or single-user installation (your choice)
- Tell [mach](mach.md) to use Nix: `export MACH_USE_NIX=`

## Dependencies for Arch { #dependencies-for-arch }
**(including Manjaro)**

<!-- https://archlinux.org/packages/ -->
- `sudo pacman -S --needed curl`

- `sudo pacman -S --needed base-devel git mesa cmake libxmu pkg-config ttf-fira-sans harfbuzz ccache llvm clang autoconf2.13 gstreamer gstreamer-vaapi gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly vulkan-icd-loader`

## Dependencies for Debian { #dependencies-for-debian }
**(including elementary OS, KDE neon, Linux Mint, Pop!_OS, Raspbian, TUXEDO OS, Ubuntu)**

<!-- https://packages.debian.org -->
<!-- https://packages.ubuntu.com -->
- `sudo apt install curl`

<!-- see python/servo/platform/linux.py in servo for how to update this -->
<!-- be sure to *remove* `libgstreamer-plugins-good1.0-dev` from this list, due to the note below -->
- `sudo apt install build-essential ccache clang cmake curl g++ git gperf libdbus-1-dev libfreetype6-dev libgl1-mesa-dri libgles2-mesa-dev libglib2.0-dev gstreamer1.0-plugins-good gstreamer1.0-plugins-bad libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-ugly gstreamer1.0-plugins-base libgstreamer-plugins-base1.0-dev gstreamer1.0-libav libgstrtspserver-1.0-dev gstreamer1.0-tools libges-1.0-dev libharfbuzz-dev liblzma-dev libudev-dev libunwind-dev libvulkan1 libx11-dev libxcb-render0-dev libxcb-shape0-dev libxcb-xfixes0-dev libxmu-dev libxmu6 libegl1-mesa-dev llvm-dev m4 xorg-dev libxkbcommon0 libxkbcommon-x11-0 tshark`

**Note:** For Ubuntu-based distributions, ensure that you also include the `libgstreamer-plugins-good1.0-dev` package alongside the packages listed above.

## Dependencies for Fedora { #dependencies-for-fedora }

<!-- see python/servo/platform/linux.py in servo for how to update this -->
* `sudo dnf install libtool gcc-c++ libXi-devel freetype-devel libunwind-devel mesa-libGL-devel mesa-libEGL-devel glib2-devel libX11-devel libXrandr-devel gperf fontconfig-devel cabextract ttmkfdir expat-devel rpm-build cmake libXcursor-devel libXmu-devel dbus-devel ncurses-devel harfbuzz-devel ccache clang clang-libs llvm python3-devel gstreamer1-devel gstreamer1-plugins-base-devel gstreamer1-plugins-good gstreamer1-plugins-bad-free-devel gstreamer1-plugins-ugly-free libjpeg-turbo-devel zlib-ng libjpeg-turbo vulkan-loader libxkbcommon libxkbcommon-x11 wireshark-cli`

## Dependencies for Gentoo { #dependencies-for-gentoo }

<!-- https://packages.gentoo.org -->
- `sudo emerge net-misc/curl media-libs/freetype media-libs/mesa dev-util/gperf dev-libs/openssl media-libs/harfbuzz dev-util/ccache sys-libs/libunwind x11-libs/libXmu x11-base/xorg-server sys-devel/clang media-libs/gstreamer media-libs/gst-plugins-base media-libs/gst-plugins-good media-libs/gst-plugins-bad media-libs/gst-plugins-ugly media-libs/vulkan-loader`

## Dependencies for openSUSE { #dependencies-for-opensuse }

<!-- https://search.opensuse.org/packages/ -->
- `sudo zypper install libX11-devel libexpat-devel Mesa-libEGL-devel Mesa-libGL-devel cabextract cmake dbus-1-devel fontconfig-devel freetype-devel gcc-c++ git glib2-devel gperf harfbuzz-devel libXcursor-devel libXi-devel libXmu-devel libXrandr-devel libopenssl-devel rpm-build ccache llvm-clang libclang autoconf213 gstreamer-devel gstreamer-plugins-base-devel gstreamer-plugins-good gstreamer-plugins-bad-devel gstreamer-plugins-ugly vulkan-loader libvulkan1`

## Dependencies for Void Linux { #dependencies-for-void-linux }

<!-- https://voidlinux.org/packages/ -->
<!-- see python/servo/platform/linux.py in servo for how to update this -->
* `sudo xbps-install libtool gcc libXi-devel freetype-devel libunwind-devel MesaLib-devel glib-devel pkg-config libX11-devel libXrandr-devel gperf bzip2-devel fontconfig-devel cabextract expat-devel cmake cmake libXcursor-devel libXmu-devel dbus-devel ncurses-devel harfbuzz-devel ccache glu-devel clang gstreamer1-devel gst-plugins-base1-devel gst-plugins-good1 gst-plugins-bad1-devel gst-plugins-ugly1 vulkan-loader libxkbcommon libxkbcommon-x11`
