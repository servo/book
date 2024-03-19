<!-- TODO: needs copyediting -->

# Tests

This is boring.
But your PR won't get accepted without a test.
Tests are located in the `tests` directory.
You'll see that there are a lot of files in there, so finding the proper location for your test is not always obvious.

First, look at the "Testing" section in `./mach --help` to understand the different test categories.
You'll also find some `update-*` commands.
It's used to update the list of expected results.

To run a test:

```
./mach test-wpt tests/wpt/yourtest
```

For your PR to get accepted, source code also has to satisfy certain tidiness requirements.

To check code tidiness:

```
./mach test-tidy
```

### Updating a test

In some cases, extensive tests for the feature you're working on already exist under tests/wpt:

- Make a release build
- run `./mach test-wpt --release --log-raw=/path/to/some/logfile`
- run [`update-wpt` on it](https://github.com/servo/servo/blob/main/tests/wpt/README.md#updating-test-expectations)

This may create a new commit with changes to expectation ini files.
If there are lots of changes, it's likely that your feature had tests in wpt already.

Include this commit in your pull request.

### Add a new test

If you need to create a new test file, it should be located in `tests/wpt/mozilla/tests` or in `tests/wpt/web-platform-tests` if it's something that doesn't depend on servo-only features.
You'll then need to update the list of tests and the list of expected results:

```
./mach test-wpt --manifest-update
```

### Debugging a test

See the [debugging guide](./debugging.md) to get started in how to debug Servo.
