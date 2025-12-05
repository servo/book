# Building for Linux

- Install `curl`:
  - Arch: `sudo pacman -S --needed curl`
  - Debian, Ubuntu: `sudo apt install curl`
  - Fedora: `sudo dnf install curl`
  - Gentoo: `sudo emerge net-misc/curl`
- Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh` 
- Install `rustup`: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Restart your shell to make sure `cargo` is available
- Install the other dependencies: `./mach bootstrap`
- Build servoshell: `./mach build`

## Unsupported Distributions 

If `./mach boostrap` reports that your distribution is unsupported, then you will need to install dependencies manually.
Below you will find instructions for installing build dependencies on a variety of types of distrubtions.
If your distribution is not listed, it's recommended that you try to adapt the list for the package names on your system.
Updates to this list are very welcome!

### Arch and Manjaro { #dependencies-for-arch }

<!-- https://archlinux.org/packages/ -->
- `sudo pacman -S --needed curl`

- `sudo pacman -S --needed base-devel git mesa cmake libxmu pkg-config ttf-fira-sans harfbuzz ccache llvm clang autoconf2.13 gstreamer gstreamer-vaapi gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly vulkan-icd-loader wireshark-cli`

### Debian-like{ #dependencies-for-debian }
**(including elementary OS, KDE neon, Linux Mint, Pop!_OS, Raspbian, TUXEDO OS, Ubuntu)**

<!-- https://packages.debian.org -->
<!-- https://packages.ubuntu.com -->
- `sudo apt install curl`

<!-- see python/servo/platform/linux.py in servo for how to update this -->
<!-- be sure to *remove* `libgstreamer-plugins-good1.0-dev` from this list, due to the note below -->
- `sudo apt install build-essential ccache clang cmake curl g++ git gperf libdbus-1-dev libfreetype6-dev libgl1-mesa-dri libgles2-mesa-dev libglib2.0-dev gstreamer1.0-plugins-good gstreamer1.0-plugins-bad libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-ugly gstreamer1.0-plugins-base libgstreamer-plugins-base1.0-dev gstreamer1.0-libav libgstrtspserver-1.0-dev gstreamer1.0-tools libges-1.0-dev libharfbuzz-dev liblzma-dev libudev-dev libunwind-dev libvulkan1 libx11-dev libxcb-render0-dev libxcb-shape0-dev libxcb-xfixes0-dev libxmu-dev libxmu6 libegl1-mesa-dev llvm-dev m4 xorg-dev libxkbcommon0 libxkbcommon-x11-0 tshark`

**Note:** For Ubuntu-based distributions, ensure that you also include the `libgstreamer-plugins-good1.0-dev` package alongside the packages listed above.

### Fedora-like { #dependencies-for-fedora }

<!-- see python/servo/platform/linux.py in servo for how to update this -->
* `sudo dnf install libtool gcc-c++ libXi-devel freetype-devel libunwind-devel mesa-libGL-devel mesa-libEGL-devel glib2-devel libX11-devel libXrandr-devel gperf fontconfig-devel cabextract ttmkfdir expat-devel rpm-build cmake libXcursor-devel libXmu-devel dbus-devel ncurses-devel harfbuzz-devel ccache clang clang-libs llvm python3-devel gstreamer1-devel gstreamer1-plugins-base-devel gstreamer1-plugins-good gstreamer1-plugins-bad-free-devel gstreamer1-plugins-ugly-free libjpeg-turbo-devel zlib-ng libjpeg-turbo vulkan-loader libxkbcommon libxkbcommon-x11 wireshark-cli`

## Gentoo-like { #dependencies-for-gentoo }

<!-- https://packages.gentoo.org -->
- `sudo emerge net-misc/curl media-libs/freetype media-libs/mesa dev-util/gperf dev-libs/openssl media-libs/harfbuzz dev-util/ccache sys-libs/libunwind x11-libs/libXmu x11-base/xorg-server sys-devel/clang media-libs/gstreamer media-libs/gst-plugins-base media-libs/gst-plugins-good media-libs/gst-plugins-bad media-libs/gst-plugins-ugly media-libs/vulkan-loader`

## openSUSE { #dependencies-for-opensuse }

<!-- https://search.opensuse.org/packages/ -->
- `sudo zypper install libX11-devel libexpat-devel Mesa-libEGL-devel Mesa-libGL-devel cabextract cmake dbus-1-devel fontconfig-devel freetype-devel gcc-c++ git glib2-devel gperf harfbuzz-devel libXcursor-devel libXi-devel libXmu-devel libXrandr-devel libopenssl-devel rpm-build ccache llvm-clang libclang autoconf213 gstreamer-devel gstreamer-plugins-base-devel gstreamer-plugins-good gstreamer-plugins-bad-devel gstreamer-plugins-ugly vulkan-loader libvulkan1`

## Void Linux { #dependencies-for-void-linux }

<!-- https://voidlinux.org/packages/ -->
<!-- see python/servo/platform/linux.py in servo for how to update this -->
* `sudo xbps-install libtool gcc libXi-devel freetype-devel libunwind-devel MesaLib-devel glib-devel pkg-config libX11-devel libXrandr-devel gperf bzip2-devel fontconfig-devel cabextract expat-devel cmake cmake libXcursor-devel libXmu-devel dbus-devel ncurses-devel harfbuzz-devel ccache glu-devel clang gstreamer1-devel gst-plugins-base1-devel gst-plugins-good1 gst-plugins-bad1-devel gst-plugins-ugly1 vulkan-loader libxkbcommon libxkbcommon-x11`

## Troubleshooting

Be sure to look at the [General Troubleshooting](general-troubleshooting.md) section if you have trouble with your build and your problem is not listed below.

<pre><blockquote><samp>build: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.39' not found</samp></blockquote></pre>

This workaround is applicable when building Servo using `nix` in Linux distributions other than NixOS.
The error indicates that the version of glibc included in the distribution is older than the one in nixpkgs.

At the end of the `shell.nix`, change the line `if ! [ -e /etc/NIXOS ]; then` to `if false; then` to disable the support in shell.nix for producing binary artifacts that don't depend on the nix store.
