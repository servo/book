# Requesting crate releases

In addition to creating the Servo browser engine, the Servo project also publishes modular components when they can benefit the wider community of Rust developers.
An example of one of these crates is [`rust-url`](https://crates.io/crates/url).
While we strive to be good maintainers, managing the process of building a browser engine and a collection of external libraries can be a lot of work, thus we make no guarantees about regular releases for these modular crates.

If you feel that a release for one of these crates is due, we will respond to requests for new releases.
The process for requesting a new release is:

1. Create one or more pull requests that prepare the crate for the new release.
2. Create a pull request that increases the version number in the repository, being careful to keep track of what component of the version should increase since the last release. This means that you may need to note if there are any breaking changes.
3. In the pull request ask that a new version be released. The person landing the change has the responsibility to publish the new version or explain why it cannot be published with the landing of the pull request.
