# Building for Windows

- Download [`uv`](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer), [`choco`](https://chocolatey.org/install#individual), and [`rustup`](https://win.rustup.rs/)
  - Be sure to select *Quick install via the Visual Studio Community installer*
- In the Visual Studio Installer, ensure the following components are installed:
  - **Windows 10/11 SDK (anything >= 10.0.19041.0)** (`Microsoft.VisualStudio.Component.Windows{10, 11}SDK.{>=19041}`)
  - **MSVC v143 - VS 2022 C++ x64/x86 build tools (Latest)** (`Microsoft.VisualStudio.Component.VC.Tools.x86.x64`)
  - **C++ ATL for latest v143 build tools (x86 & x64)** (`Microsoft.VisualStudio.Component.VC.ATL`)
- Restart your shell to make sure `cargo` is available
- Install the other dependencies: `.\mach bootstrap`
- Build servoshell: `.\mach build`

<div class="warning _note">

**We don’t recommend having more than one version of Visual Studio installed.**
Servo will try to search for the appropriate version of Visual Studio, but having only a single version installed means fewer things can go wrong.
</div>

## Troubleshooting

Be sure to look at the [General Troubleshooting](general-troubleshooting.md) section if you have trouble with your build and your problem is not listed below.


<pre><blockquote><samp><a href="https://github.com/servo/servo/blob/d9f067e998671d16a0274c2a7c8227fec96a4607/python/mach_bootstrap.py#L179">Cannot run mach in a path on a case-sensitive file system on Windows.</a></samp></blockquote></pre>

- Open a command prompt or PowerShell as administrator (Win+X, A)
- Disable case sensitivity for your Servo repo:<br>
  `fsutil file SetCaseSensitiveInfo X:\path\to\servo disable`
  
<pre><blockquote><samp><a href="https://github.com/servo/servo/blob/d86e713a9cb5be2555d63bd477d47d440fa8c832/python/servo/build_commands.py#L460">Could not find DLL dependency: </a>api-ms-win-crt-runtime-l1-1-0.dll</samp></blockquote><blockquote><samp><a href="https://github.com/servo/servo/blob/f76982e2e7f411e2e2fd8e6dbfe92a080acefc54/python/servo/build_commands.py#L531">DLL file `</a>api-ms-win-crt-runtime-l1-1-0.dll<a href="https://github.com/servo/servo/blob/f76982e2e7f411e2e2fd8e6dbfe92a080acefc54/python/servo/build_commands.py#L531">` not found!</a></samp></blockquote></pre>

Find the path to `Redist\ucrt\DLLs\x64\api-ms-win-crt-runtime-l1-1-0.dll`, e.g. `C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64\api-ms-win-crt-runtime-l1-1-0.dll`.

Then set the `WindowsSdkDir` environment variable to the path that contains `Redist`, e.g. `C:\Program Files (x86)\Windows Kits\10`.

<pre><blockquote><samp>thread 'main' panicked at 'Unable to find libclang: "couldn\'t find any valid shared libraries matching: [\'clang.dll\', \'libclang.dll\'], set the `LIBCLANG_PATH` environment variable to a path where one of these files can be found (invalid: [(C:\\Program Files\\LLVM\\bin\\libclang.dll: <strong>invalid DLL (64-bit)</strong>)])"', C:\Users\me\.cargo\registry\src\...</samp></blockquote></pre>

rustup may have been installed with the 32-bit default host, rather than the 64-bit default host needed by Servo.
Check your default host with `rustup show`, then set the default host:

`> rustup set default-host x86_64-pc-windows-msvc`

<pre><blockquote><samp><a href="https://searchfox.org/mozilla-central/rev/058ab60e5020d7c5c98cf82d298aa84626e0cd79/build/moz.configure/util.configure#143-147">ERROR: <strong>GetShortPathName returned a long path name:</strong> `</a>C:/PROGRA~2/Windows Kits/10/<a href="https://searchfox.org/mozilla-central/rev/058ab60e5020d7c5c98cf82d298aa84626e0cd79/build/moz.configure/util.configure#143-147">`. Use `fsutil file setshortname' to create a short name for any components of this path that have spaces.</a></samp></blockquote></pre>

SpiderMonkey (mozjs) requires [8.3 filenames](https://en.wikipedia.org/wiki/8.3_filename) to be enabled on Windows ([#26010](https://github.com/servo/servo/issues/26010)).

- Open a command prompt or PowerShell as administrator (Win+X, A)
- Enable 8.3 filename generation: `fsutil behavior set disable8dot3 0`
- Uninstall and reinstall whatever contains the failing paths, such as Visual Studio or the Windows SDK — this is easier than adding 8.3 filenames by hand

<pre><blockquote><samp><a href="https://servo.zulipchat.com/#narrow/channel/263398-general/topic/Build.20issues/near/507644362">= note: lld-link: error: undefined symbol: __std_search_1
>>> referenced by D:\a\mozjs\mozjs\mozjs-sys\mozjs\intl\components\src\NumberFormatterSkeleton.cpp:157</a></samp></blockquote></pre>

Issues like this can occur when mozjs is upgraded, as the update may depend on newer MSVC (remember we require "Latest" in [set up your environment](setting-up-your-environment.md#tools-for-windows)!).  To resolve it, launch the Visual Studio Installer and apply all available updates.
