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
        <th></th>
        <th>debug</th>
        <th>release</th>
        <th>production</th>
    </tr>
</thead>
<tbody>
    <tr>
        <th>mach option</th>
        <td><code>-d<br>--debug</code></td>
        <td><code>-r<br>--release</code></td>
        <td><code>--prod<br>--production</code></td>
    </tr>
    <tr>
        <th>optimised?</th>
        <td><a href="https://doc.rust-lang.org/cargo/reference/profiles.html#dev">no</a></td>
        <td><a href="https://github.com/servo/servo/blob/457d37d94ee6966cad377c373d333a00c637e1ae/Cargo.toml#L153">yes</a></td>
        <td>yes, <a href="https://github.com/servo/servo/blob/9457a40ca2cd4b9530ba7c5334c82f3b3f2e7ac8/Cargo.toml#L177-L182">more than</a> in <strong>release</strong></td>
    </tr>
    <tr>
        <th>maximum RUST_LOG level</th>
        <td><code>trace</code></td>
        <td><code>info</code></td>
        <td><code>info</code></td>
    </tr>
    <tr>
        <th>debug assertions?</th>
        <td>yes</td><td>yes(!)</td><td>no</td>
    </tr>
    <tr>
        <th>debug info?</th>
        <td>yes</td><td>no</td><td>no</td>
    </tr>
    <tr>
        <th>symbols?</th>
        <td>yes</td><td>no</td><td>yes</td>
    </tr>
    <tr>
        <th>finds resources in<br>current working dir?</th>
        <td>yes</td><td>yes</td><td>no(!)</td>
    </tr>
</tbody>
</table>

There are also two special variants of production builds for performance-related use cases:

- `production-stripped` builds are ideal for benchmarking Servo over time, with debug symbols stripped for faster initial startup
- `profiling` builds are ideal for [profiling](profiling.md) and troubleshooting performance issues; they behave like a debug or release build, but have the same performance as a production build

<table>
<thead>
    <tr>
        <th></th>
        <th>production</th>
        <th>production-stripped</th>
        <th>profiling</th>
    </tr>
</thead>
<tbody>
    <tr>
        <th>mach <code>--profile</code></th>
        <td><code>production</code></td>
        <td><code>production-stripped</code></td>
        <td><code>profiling</code></td>
    </tr>
    <tr>
        <th>debug info?</th>
        <td>no</td><td>no</td><td>yes</td>
    </tr>
    <tr>
        <th>symbols?</th>
        <td>yes</td><td>no</td><td>yes</td>
    </tr>
    <tr>
        <th>finds resources in<br>current working dir?</th>
        <td>no</td><td>no</td><td>yes(!)</td>
    </tr>
</tbody>
</table>

You can change these settings in a servobuild file (see [servobuild.example](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/servobuild.example)) or in the root [Cargo.toml](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/Cargo.toml).

## Optional build settings

Some build settings can only be enabled manually:

- **AddressSanitizer builds** are enabled with `./mach build --with-asan`
- **crown linting** is recommended when hacking on DOM code, and is enabled with `./mach build --use-crown`
- **SpiderMonkey debug builds** are enabled with `./mach build --debug-mozjs`, or `[build] debug-mozjs = true` in your servobuild file

A full list of arguments can be seen by running `./mach build --help`.

## Running servoshell

When you build it yourself, servoshell will be in `target/debug/servo` or `target/release/servo`.
You can run it directly as shown above, but we recommend using [mach](hacking/mach.md) instead.

To run servoshell with mach, replace `./servo` with `./mach run -d --` or `./mach run -r --`, depending on the [build profile](hacking/building-servo.md) you want to run.
For example, both of the commands below run the debug build of servoshell with the same options:

```sh
$ target/debug/servo https://demo.servo.org
$ ./mach run -d -- https://demo.servo.org
```
