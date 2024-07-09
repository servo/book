# TODO: wiki/Building

<!-- https://github.com/servo/servo/wiki/Building/95a6f67d29c58d9269c55b9128dbf863339c7502 -->

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

### Android

Please see [[Building for Android]].

## Windows Tips

### Troubleshooting the Windows Build

> If you have troubles with `x63 type` prompt as `mach.bat` set by default:
> 0. You may need to choose and launch the type manually, such as `x86_x64 Cross Tools Command Prompt for VS 2019` in the Windows menu.)
> 1. `cd to/the/path/servo`
> 2. `python mach build -d`
