# Offline Builds

Servo releases provide a `servo.tar.gz` artifact which contains Servo's source code and all Rust dependencies
vendored. The `.cargo/config.toml` file in the tarball contains the necessary configuration to build Servo
offline using the vendored dependencies.

## Linux

Please view the [Linux build instructions](./linux.md) for more on installing the required build dependencies.
We generally recommend using `./mach build` to build Servo, however that does require `uv` to be installed and the
Python dependencies to be synced via `uv sync` in advance (otherwise `./mach` will try to access the network to setup the python environment). 
```shell
# online pre-build environment (e.g. building a docker container)
uv sync
# offline build environment
./mach build --profile=production --frozen
```

In cases where this is difficult, you can also build Servo using `cargo`, in which case any recent Python version (>= 3.11) should be sufficient (but this is not tested in CI).
Note that `./mach build` will enable the `media-gstreamer` feature by default - When using `cargo` you need to enable this feature manually, and set any gstreamer-related environment variables as well.
The required environment variables for the gstreamer feature are not documented here, but documentation improvements based on our `./mach build` code are welcome.

```shell
# Build an offline release build with the production profile.
cargo build --profile=production --frozen
```




## Windows and MacOS

On Windows and MacOS, `./mach bootstrap` will download additional dependencies necessary to build Servo.
These are currently not provided in the tarball. 
If there is interest in offline builds for these platforms, contributions are welcome (but reach out first on Zulip or via GitHub issues).


## Prebuilt SpiderMonkey artifacts

Online builds use prebuilt SpiderMonkey artifacts by default, hosted on [servo/mozjs](https://github.com/servo/mozjs)'s GitHub releases.
If you want to simplify or speed-up your build environment, you can pre-download these artifacts yourself and use `MOZJS_ARCHIVE=path/to/libmozjs.tar.gz` to use the prebuilt artifacts in offline builds.
You can verify the integrity of the downloaded artifacts by using [GitHub attestions] with the `gh` tool:

```shell
gh attestion verify path/to/libmozjs.tar.gz -R servo/mozjs
```

[GitHub attestions]: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations