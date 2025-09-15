# Building Servo

<div class="warning _note">

**If this is your first time building Servo**, be sure to [set up your environment](setting-up-your-environment.md) before continuing with the steps below.
</div>

To build servoshell for your machine:

```sh
$ ./mach build [profile]
```
<div class="warning _note">

There are multiple [profiles](#build-profiles) available for build. **debug** is default profile if no profile is passed.
</div>

To build servoshell for cross-compilation target:

```sh
$ ./mach build [--android/--ohos] [profile]
```
<div class="warning _note">

Refer the extra setup required for [Android](building-for-android.md) and [OpenHarmony](building-for-openharmony.md) builds.
</div>

To check your code for compile errors, without a full build:

```sh
$ ./mach check
```

<div class="warning _note">

**Sometimes the tools or dependencies needed to build Servo will change.**
If you start encountering build problems after updating Servo, try running `./mach bootstrap` again, or [set up your environment](setting-up-your-environment.md) from the beginning.

**You are not alone!**
If you have problems building Servo that you can’t solve, you can always ask for help in the [build issues](https://servo.zulipchat.com/#narrow/stream/263398-general/topic/Build.20Issues) chat on Zulip.
</div>

## Build profiles

There are three main build profiles, which you can build and use independently of one another:

- debug builds, which allow you to use a debugger (lldb) (selected by default if no profile is passed)
- release builds, which are slower to build but more performant
- production builds, which are used for official releases only

<table>
<thead>
    <tr>
        <th>
        <th>debug
        <th>release
        <th>production
<tbody>
    <tr>
        <th>mach option
        <td><code>-d<br>--debug</code>
        <td><code>-r<br>--release</code>
        <td><code>--prod<br>--production</code>
    <tr>
        <th>optimised?
        <td><a href="https://doc.rust-lang.org/cargo/reference/profiles.html#dev">no</a>
        <td><a href="https://github.com/servo/servo/blob/457d37d94ee6966cad377c373d333a00c637e1ae/Cargo.toml#L153">yes</a>
        <td>yes, <a href="https://github.com/servo/servo/blob/9457a40ca2cd4b9530ba7c5334c82f3b3f2e7ac8/Cargo.toml#L177-L182">more than</a> in <strong>release</strong>
    <tr>
        <th>maximum RUST_LOG level
        <td><code>trace</code>
        <td><code>info</code>
        <td><code>info</code>
    <tr>
        <th>debug assertions?
        <td>yes<td>yes(!)<td>no
    <tr>
        <th>debug info?
        <td>yes<td>no<td>no
    <tr>
        <th>symbols?
        <td>yes<td>no<td>yes
    <tr>
        <th>finds resources in<br>current working dir?
        <td>yes<td>yes<td>no(!)
</table>

There are also two special variants of production builds for performance-related use cases:

- `production-stripped` builds are ideal for benchmarking Servo over time, with debug symbols stripped for faster initial startup
- `profiling` builds are ideal for [profiling](profiling.md) and troubleshooting performance issues; they behave like a debug or release build, but have the same performance as a production build

<table>
<thead>
    <tr>
        <th>
        <th>production
        <th>production-stripped
        <th>profiling
<tbody>
    <tr>
        <th>mach <code>--profile</code>
        <td><code>production</code>
        <td><code>production-stripped</code>
        <td><code>profiling</code>
    <tr>
        <th>debug info?
        <td>no<td>no<td>yes
    <tr>
        <th>symbols?
        <td>yes<td>no<td>yes
    <tr>
        <th>finds resources in<br>current working dir?
        <td>no<td>no<td>yes(!)
</table>

You can change these settings in a servobuild file (see [servobuild.example](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/servobuild.example)) or in the root [Cargo.toml](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/Cargo.toml).

## Optional build settings

Some build settings can only be enabled manually:

- **AddressSanitizer builds** are enabled with `./mach build --with-asan`
- **crown linting** is recommended when hacking on DOM code, and is enabled with `./mach build --use-crown`
- **SpiderMonkey debug builds** are enabled with `./mach build --debug-mozjs`, or `[build] debug-mozjs = true` in your servobuild file

A full list of arguments can be seen by running `./mach build --help`.
