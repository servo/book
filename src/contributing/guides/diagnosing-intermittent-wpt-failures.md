# Diagnosing Intermittent Failures in Web Platform Tests

The most common sources of intermittent failures in Web Platform Tests include:

* Scheduling (e.g. multiple threads running concurrently or in parallel)
* OS interactions (e.g. socket read/write for network requests)
* Nondeterministic task selection

Each of these can perturb the ordering of events within Servo in nondeterministic ways, exposing unexpected or unplanned behaviour in the engine.

In Servo, this nondeterminism often manifests in code that:

* uses mutexes or shared memory instead of channels
* enqueues multiple tasks that run on one thread but via different task sources
* uses timeouts to detect if an event occured

## Reproducing the failure

While it's possible to come up with a theory for a particular intermittent failure, it is helpful to show a before/after failure rate for an attempted fix.

Some strategies for reproducing intermittent failures:
* run with `--repeat-until-unexpected` to repeat the test until an unexpected result is reported
* run the test under heavy load (e.g. run a clean release build in another terminal while running the test on repeat)
* try different build or runtime configurations:
  * `./mach build --dev`
  * `./mach build --release`
  * `./mach build --debug-mozjs`
  * `./mach test-wpt ... --binary-args=--force-ipc`
  * `./mach test-wpt ... --binary-args=--multiprocess`

Make sure your `test-wpt` command is using the same runtime binary as the build you have made!

## Diagnosing the problem

Once you have reproduced the failure, you need to figure out what's different about the runs that report different results.
When testing out changes, you should keep in mind the frequency of the intermittent results.
Don't jump to conclusions without waiting long enough!

Start by commenting out as much of the test as you can while still reproducing the failure.

Try adding `console.log` calls to show the ordering of different events, then compare the output between the common case and the intermittent case.
You may need to use [set the `RUST_LOG` environment variable](../debugging.md#debug-logging-with-log-and-rust_log) to see internal Servo tracing logs for relevant crates and modules.

[Add explicit delays](#adding-delays) to parts of the test to observe if the failures are more or less likely to occur.

### Adding delays

Consider moving part of the test into a closure that executes after a fixed delay, like `test_object.step_timeout(() => ..., 1000)`.

If there is a network request for a particular URL, you can easily [add a delay](https://web-platform-tests.org/writing-tests/server-pipes.html#trickle) to the response.

## Diagnosing problems with layout tests

If the test verifies properties of layout (either a reftest or a test that uses layout APIs like `getBoundingClientRect()`, `scrollTop`, `offsetParent`, etc.), somce common sources of intermittent results include:

1. incremental layout behaves incorrectly for a particular change, but this is covered up by another async operation that triggers additional layout
2. a screenshot is taken too early/too late relative to some other change (e.g. a web font loading)

To make incremental layout issues more visible, try:
* delaying the page modification until all other page updates are complete (try a very delayed `setTimeout`)
* run the test with a real window (`--no-headless`)
* do not touch the mouse until the page modification occurs, then resize the window

To identify if screenshot timing is an issue, use the [reftest analyzer](../testing.md#analyzing-reftest-results) to see the screenshot received by the test harness.
If it does not match the output you see when [running the test file](diagnosing-expected-wpt-failures.md#diagnosing-a-reftest-failure), the timing of the screenshot may be at fault.
