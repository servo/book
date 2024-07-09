# Building Servo

<div class="warning _note">

**If this is your first time building Servo**, be sure to [set up your environment](setting-up-your-environment.md) before continuing with the steps below.
</div>

To build servoshell for your machine:

```sh
$ ./mach build -d
```

To build servoshell for Android (armv7):

```sh
$ ./mach build --android
```

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

- debug builds, which allow you to use a debugger (lldb)
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
        <td><code>-d</code>
        <td><code>-r</code>
        <td><code>--profile production</code>
    <tr>
        <th>optimised?
        <td>no<td>yes<td>yes
    <tr>
        <th>debug info?
        <td>yes<td>no<td>no
    <tr>
        <th>debug assertions?
        <td>yes<td>yes(!)<td>no
    <tr>
        <th>maximum RUST_LOG level
        <td><code>trace</code><td><code>info</code><td><code>info</code>
    <tr>
        <th>finds resources in<br>current working dir?
        <td>yes<td>yes<td>no
</table>

You can change these settings in a servobuild file (see [servobuild.example](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/servobuild.example)) or in the root [Cargo.toml](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/Cargo.toml).

## Optional build settings

Some build settings can only be enabled manually:

- **AddressSanitizer builds** are enabled with `./mach build --with-asan`
- **crown linting** is recommended when hacking on DOM code, and is enabled with `./mach build --use-crown`
- **SpiderMonkey debug builds** are enabled with `./mach build --debug-mozjs`, or `[build] debug-mozjs = true` in your servobuild file
