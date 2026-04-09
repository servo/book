# Servo LTS releases

Besides our monthly releases, the servo community provides a best-effort long term support (LTS) release.
Since Servos public API is still evolving, embedders that have limited resources to stay up to date with the latest Servo release, may prefer to use the LTS release.
This allows them to have scheduled upgrade timeframes, and benefit from security fixes (including security fixes of our JavaScript engine).

## Scope of the LTS release

**Servo is provided AS IS and no specific guarantees are given**. 
The LTS releases (and the bullet points below) are provided on a best-effort basis.

- A new LTS release / branch is introduced every 6 months, based on the current regular release at the time.
- The expected support duration is 9 months, giving embedders time to migrate to the next LTS release.
- The LTS release will receive security fixes only.
- Patch releases will be released as needed, there is no fixed schedule.
- Only the `servo` library and dependencies are in scope.
  The browser demo `ServoShell` is explicitly out of scope.
- The minimum supported Rust version (MSRV) will not be bumped during the LTS release cycle.
- Releases will be published to crates.io **if possible**, but embedders should expect that `git` dependencies might be required.

## Patching CVEs in downstream crates

Many Rust libraries generally don't backport CVE fixes to older releases / branches.
Since MSRV increases are treated as breaking changes, this can lead to us being unable to upgrade to a released newer version of a library (which patches the CVE).
These situations will be handled on a case-by-case basis, ideally in cooperation with the upstream maintainer, and will likely involve pulling a patched version of the library via `git`.
This means that LTS patch releases of servo shouldn't be expected to be avaiable on crates.io, since they could have `git` dependencies.

## Limitations

- Servo is provided AS IS and no specific security guarantees are given.
  The LTS releases are provided on a best-effort basis by interested community members.
- As mentioned above servo does not have a 1.0 release yet, which means that production usage of servo should be carefully evaluated.
  The risk profile of using servo in an app to render known, trusted content is very different from using servo as a browser to render arbitrary content.

## LTS release maintainers

- @jschwe (Jonathan Schwender)
- TBD
