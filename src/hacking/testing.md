<!-- TODO: needs copyediting -->

# Automated testing

This is boring.
But your PR won't get accepted without a test.

There are three types of tests in servo.
- Code formatting tests (`./mach test-tidy`).
- Unit tests (`./mach test-unit`).
- End to End tests (`./mach test-wpt`).

The focus of this document will be on End 2 End tests but we want to mention the other tests first.

Every submission has to confirm to the code formatting tests. Most of the formatting can be done
automatically with `./mach fmt`.

The unit tests are in various files throughout the code base in typical rust `#[(cfg(test))]` and
with `#[test]` annotations. If you are debugging a test you can use cargo's feature to run only one test
via `cargo test test_fn_name` and `cargo test test_fn_name -- --exact`, or if it is in a module
`cargo test test_mod_name::test_fn_name -- --exact` (e.g., `cargo test -p net
test_fetch_response_is_not_network_error`).
Running the whole test-suite can be very memory intensive, you can dampen this behaviour somewhat with
with restricting the amount of compiled crates with `./mach test-unit -j 4`.


## End 2 End Tests
Tests are located in the `tests` directory.
You'll see that there are a lot of files in there, so finding the proper location for your test is not always obvious.

First, look at the "Testing" section in `./mach --help` to understand the different test categories.
You'll also find some `update-*` commands.
It's used to update the list of expected results.

To run a test:

```
./mach test-wpt tests/wpt/yourtest
```

## Updating a test

In some cases, extensive tests for the feature you're working on already exist under tests/wpt:

- Make a release build
- run `./mach test-wpt --release --log-raw=/path/to/some/logfile`
- run [`update-wpt` on it](#updating-web-test-expectations)

This may create a new commit with changes to expectation ini files.
If there are lots of changes, it's likely that your feature had tests in wpt already.

Include this commit in your pull request.

## Add a new test

If you need to create a new test file, it should be located in `tests/wpt/mozilla/tests` or in `tests/wpt/web-platform-tests` if it's something that doesn't depend on servo-only features.
You'll then need to update the list of tests and the list of expected results:

```
./mach test-wpt --manifest-update
```

## Debugging a test

See the [debugging guide](./debugging.md) to get started in how to debug Servo.

## Web Platform Tests (`tests/wpt`)

This folder contains the Web Platform Tests and the code required to integrate them with Servo.
In addition, there are WebGPU and WebGL tests which are imported and converted into Web Platform Test style tests.

### Contents of `tests/wpt`

In particular, this folder contains:

* `config.ini`: some configuration for the Web Platform Tests
* `include.ini`: the subset of Web Platform Tests we currently run
* `tests`: In-tree copy of the Web Platform Tests
* `meta`: expected failures for the Web Platform tests we run
* `mozilla`: Web Platform Test-style tests that cannot be upstreamed
* `webgl`: The imported WebGL tests
* `webgpu`: The imported WebGPU tests

## Running the Web Platform Tests

The simplest way to run the Web Platform Tests in Servo is `./mach test-wpt` in the root directory.
This will run the subset of JavaScript tests defined in `include.ini` and log the output to stdout.

A subset of tests may be run by providing positional arguments to the mach command, either as filesystem paths or as test urls e.g.

    ./mach test-wpt tests/wpt/tests/dom/historical.html

to run the dom/historical.html test, or

    ./mach test-wpt dom

to run all the DOM tests.

There are also a large number of command line options accepted by the test harness; these are documented by running with `--help`.

Running the WPT tests with a debug build often results in timeouts.
Instead, consider building with `mach build -r` and testing with `mach test-wpt -r`.

### Running Web Platform Tests on your GitHub fork

Alternatively, you can execute the tests on GitHub-hosted runners using `mach try`.
Usually, `mach try linux-wpt` (all tests, linux) will be enough.

You can view the run results in your fork under the "Actions" tab.
Any failed tasks will include a list of stable unexpected results at the bottom of the log.
Unexpected results that are known-intermittent can likely be ignored.

When opening a PR, you can include a link to the run. Otherwise, reviewers will run the tests again.

### Running the Web Platform Tests with an external server

Normally wptrunner starts its own WPT server, but occasionally you might want to run multiple instances of `mach test-wpt`, such as when debugging one test while running the full suite in the background, or when running a single test many times in parallel (--processes only works across different tests).

This would lead to a “Failed to start HTTP server” errors, because you can only run one WPT server at a time.
To fix this:

1. Follow the steps in [**Running web tests manually**](#running-web-tests-manually)
2. Add a `break` to [start_servers in serve.py](https://github.com/servo/servo/blob/ce92b7bfbd5855aac18cb4f8a8ec59048041712e/tests/wpt/web-platform-tests/tools/serve/serve.py#L745-L783) as follows:
  ```
  --- a/tests/wpt/tests/tools/serve/serve.py
  +++ b/tests/wpt/tests/tools/serve/serve.py
  @@ -746,6 +746,7 @@ def start_servers(logger, host, ports, paths, routes, bind_address, config,
                     mp_context, log_handlers, **kwargs):
       servers = defaultdict(list)
       for scheme, ports in ports.items():
  +        break
           assert len(ports) == {"http": 2, "https": 2}.get(scheme, 1)

           # If trying to start HTTP/2.0 server, check compatibility
  ```
3. Run `mach test-wpt` as many times as needed

If you get unexpected TIMEOUT in testharness tests, then the custom testharnessreport.js may have been installed incorrectly (see [**Running web tests manually**](#running-web-tests-manually) for more details).


### Running Web Platform Tests manually

(See also [the relevant section of the upstream README][upstream-running].)

It can be useful to run a test without the interference of the test runner, for example when using a debugger such as `gdb`.
To do this, we need to start the WPT server manually, which requires some extra configuration.

To do this, first add the following to the system's hosts file:

    127.0.0.1   www.web-platform.test
    127.0.0.1   www1.web-platform.test
    127.0.0.1   www2.web-platform.test
    127.0.0.1   web-platform.test
    127.0.0.1   xn--n8j6ds53lwwkrqhv28a.web-platform.test
    127.0.0.1   xn--lve-6lad.web-platform.test

Navigate to `tests/wpt/web-platform-tests` for the remainder of this section.

Normally wptrunner [installs Servo’s version of testharnessreport.js][environment], but when starting the WPT server manually, we get the default version, which won’t report test results correctly.
To fix this:

1. Create a directory `local-resources`
2. Copy `tools/wptrunner/wptrunner/testharnessreport-servo.js` to `local-resources/testharnessreport.js`
3. Edit `local-resources/testharnessreport.js` to substitute the variables as follows:
  * `%(output)d`
    * → `1` if you want to play with the test interactively (≈ pause-after-test)
    * → `0` if you don’t care about that (though it’s also ok to use `1` always)
  * `%(debug)s` → `true`
4. Create a `./config.json` as follows (see `tools/wave/config.default.json` for defaults):
  ```
  {"aliases": [{
      "url-path": "/resources/testharnessreport.js",
      "local-dir": "local-resources"
  }]}
  ```

[environment]: https://github.com/servo/servo/blob/ce92b7bfbd5855aac18cb4f8a8ec59048041712e/tests/wpt/web-platform-tests/tools/wptrunner/wptrunner/environment.py#L231-L237

Then start the server with `./wpt serve`.
To check if `testharnessreport.js` was installed correctly:

* The standard output of `curl http://web-platform.test:8000/resources/testharnessreport.js` should look like [testharnessreport-servo.js], not like [the default testharnessreport.js]
* The standard output of `target/release/servo http://web-platform.test:8000/css/css-pseudo/highlight-pseudos-computed.html` (or any [testharness test]) should contain lines starting with:
    * `TEST START`
    * `TEST STEP`
    * `TEST DONE`
    * `ALERT: RESULT:`

[testharnessreport-servo.js]: https://github.com/servo/servo/blob/ce92b7bfbd5855aac18cb4f8a8ec59048041712e/tests/wpt/web-platform-tests/tools/wptrunner/wptrunner/testharnessreport-servo.js
[the default testharnessreport.js]: https://github.com/servo/servo/blob/ce92b7bfbd5855aac18cb4f8a8ec59048041712e/tests/wpt/web-platform-tests/resources/testharnessreport.js
[testharness test]: http://web-platform-tests.org/writing-tests/testharness.html

To prevent browser SSL warnings when running HTTPS tests locally, you will need to run Servo with `--certificate-path resources/cert-wpt-only`.

[upstream-running]: https://github.com/w3c/web-platform-tests#running-the-tests

### Running the Web Platform Tests in Firefox

When working with tests, you may want to compare Servo's result with Firefox.
You can supply `--product firefox` along with the path to a Firefox binary (as well as few more odds and ends) to run tests in Firefox from your Servo checkout:

    GECKO="$HOME/projects/mozilla/gecko"
    GECKO_BINS="$GECKO/obj-firefox-release-artifact/dist/Nightly.app/Contents/MacOS"
    ./mach test-wpt dom --product firefox --binary $GECKO_BINS/firefox --certutil-binary $GECKO_BINS/certutil --prefs-root $GECKO/testing/profiles

## Updating Web Platform Test expectations

When fixing a bug that causes the result of a test to change, the expected results for that test need to be changed.
This can be done manually, by editing the `.ini` file under the `meta` folder that corresponds to the test.
In this case, remove the references to tests whose expectation is now `PASS`, and remove `.ini` files that no longer contain any expectations.

When a larger number of changes is required, this process can be automated.
This first requires saving the raw, unformatted log from a test run, for example by running `./mach test-wpt --log-raw /tmp/servo.log`.
Once the log is saved, run from the root directory:

    ./mach update-wpt /tmp/servo.log

Running *all* Web Platform Tests locally will take a long time and often cause unrelated failures (such as the runner exceeding the maximum number of open files on your system).
The test expectations are also set based on the results of Servo's CI machines, so differences in your setup might cause failures.

Usually you will have a rough idea where tests for your changes are.
For example, almost all tests for [SubtleCrypto](https://github.com/servo/servo/blob/63793ccbb7c0768af3f31c274df70625abacb508/components/script/dom/subtlecrypto.rs) code are in the [`WebCryptoAPI`](https://github.com/web-platform-tests/wpt/tree/550fb109615cf434b03b30b76aa0dea6bfb0ebe1/WebCryptoAPI) directory.
In this case you can run only these tests with `./mach test-wpt WebCryptoAPI`, followed by `./mach update-wpt` as described above.
To ensure that other tests didn't break, do a [try run](#running-tests-on-your-github-fork) afterwards.

## Modifying Web Platform Tests

Please see the Web Platform Test [Writing Tests guide](https://web-platform-tests.org/writing-tests/index.html) for how to write tests.
In general, a good way to start is to follow these steps:

1. Find the directory that tests the feature you want to test.
2. Find a test in that directory that tests a similar behavior, make a copy of the test with an appropriate name, and make your modifications.
3. If the test is a reference test, you should also copy the reference if it needs to change, following the naming pattern of the directory you are modifying.
4. Run  `./mach update-manifest` to update the WPT manifest with the new tests.

You must also run `./mach update-manifest` whenever you modify a test, reference, or support file.
All changes to our in-tree Web Platform Tests will be upstreamed automatically when your PR is merged.

## Servo-specific tests

The `mozilla` directory contains tests that cannot be upstreamed for some reason (e.g. because they depend on Servo-specific APIs), as well as some legacy tests that should be upstreamed at some point.
When run they are mounted on the server under `/_mozilla/`.

## Analyzing reftest results

Reftest results can be analyzed from a raw log file.
To generate this run with the `--log-raw` option e.g.

```
./mach test-wpt --log-raw wpt.log
```

This file can then be fed into the [reftest analyzer](https://hg.mozilla.org/mozilla-central/raw-file/tip/layout/tools/reftest/reftest-analyzer-structured.xhtml) which will show all failing tests (not just those with unexpected results).
Note that this ingests logs in a different format to [original version of the tool](https://hg.mozilla.org/mozilla-central/raw-file/tip/layout/tools/reftest/reftest-analyzer.xhtml) written for gecko reftests.

The reftest analyzer allows pixel-level comparison of the test and reference screenshots.
Tests that both fail and have an unexpected result are marked with a `!`.

## Updating the WPT manifest

MANIFEST.json can be regenerated automatically with the mach command `update-manifest` e.g.

    ./mach update-manifest

This is equivalent to running

    ./mach test-wpt --manifest-update SKIP_TESTS
