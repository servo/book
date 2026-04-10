# Overview: Embedding Servo

Servo is a web browser engine, which we intend to be easy to embed in other applications.
Currently, the documentation on how to embed Servo is sparse, and this Chapter is an active work in progress.
Please feel free to reach out to us on the [Servo Zulip] chat if you have any questions.

[Servo Zulip]: https://servo.zulipchat.com

## Building servo without mach

It is possible to build servo directly with `cargo`, albeit you will likely need to reimplement some of the mach functionality.
Below is a short overview of things to keep in mind.


### Environment variables

`./mach` sets a number of environment variables to control the build, which is particularly required when cross-compiling to e.g., Android or OpenHarmony.
You can run `./mach print-env` to see which variables are set, and use that to configure your build.

### Media support

`./mach build` enables the `media-gstreamer` feature by default, which is not the case for regular builds.
`media-gstreamer` is required for media support on the common desktop platforms. 
On Linux you will need to install the required `gstreamer` libraries via your package manager (e.g. by running ./mach bootstrap).
On macOS `./mach bootstrap` will install the required `gstreamer` libraries by installing the latest packages from https://github.com/servo/servo-build-deps/releases/tag/macOS.
On Windows you can install the gstreamer libraries from https://github.com/servo/servo-build-deps/releases/tag/msvc-deps (version 1.22.8).

### Resources

Servo requires some resources, and provides default versions via the `servo-default-resources` crate if the `baked-in-resources` feature is enabled.
This is achieved by baking the resources into the binary. 
Embedders can opt-out, by disabling default-features, and providing their own resource reading mechanism via [servo_embedder_traits::submit_resource_reader].
In such a case the ResourceReader implementation is responsible for providing all resources.

[servo_embedder_traits::submit_resource_reader]: https://docs.rs/servo-embedder-traits/latest/embedder_traits/macro.submit_resource_reader.html

An example usage is the OpenHarmony port, which reads all resources from the filesystem: [ohos/resources.rs](https://github.com/servo/servo/blob/78c9fe2a4c7a645e7ec729094bfe3eb8a6c15189/ports/servoshell/egl/ohos/resources.rs).

