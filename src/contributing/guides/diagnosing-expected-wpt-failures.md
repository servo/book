# Diagnosing Expected Failures in Web Platform Tests

## Diagnosing a FAIL result

Start by opening the test file's `.ini` that contains the expected failures.
It is found under `tests/wpt/meta/` in a parallel directory tree to `tests/wpt/tests/`.

The WPT test harness suppresses most output related to failures that are marked expected in the `.ini` file.

To learn more about all failures for a test file, change the top-level `[filename.html]` so it doesn't match the actual filename; this will cause the harness to ignore the ini file entirely.

To learn more about one subtest in particular, delete it from the `.ini` file.
After changing the file as desired, run the test again.
The harness will show the specific test assertions that fail, along with the JS stack trace when the failures occur.

## Diagnosing an ERROR result

Error results occur when an exception is thrown without being caught.
The stack trace from the test harness should show the subtest in which the uncaught exception was observed, as well as the kind of error.

If the exception comes from a calling an API method that is implemented in Rust, you will need to find that method implementation and look for code that returns a matching [`Error`](https://doc.servo.org/script/dom/bindings/error/enum.Error.html) variant.

## Diagnosing a TIMEOUT result

Test timeouts occur when an async/promise subtest is declared but never completes.
You will need to identify two things:

1. the last test code that successfully runs
2. why the subsequent code that should run is never executed

The quickest way to track down the first data point is inserting `console.log` statements to prove that code paths are executed.

The code that doesn't run is usually:
* an event handler (either the event is never fired, or the handler has filtering logic that is tripped)
* a promise handler (the promise is never resolved/rejected)
* an await statement (the promise is never resolved/rejected)

In each case, it's helpful to start from the code that is intended to trigger the missing step (e.g. the relevant `event.fire(..)` in Rust code) and working backwards to determine why it's never executed.

## Diagnosing a NOTRUN result

These failures occur when an async subtest is declared (e.g. `let some_test = async_test("frobbing the whatsit");`) but never executed (e.g. `some_test.step(() => ...)`).
This usually occurs when a test file sets up many subtests and tries to run them sequentially, but encounters an exception or timeout that prevents further execution.

These results are usually a symptom of some other problem exposed by the test file, and those other problems should be investigated first.

## Diagnosing a reftest failure

To see a visual representation of the differences between a test file and its reference file, you can use the [reftest analyzer](../testing.md#analyzing-reftest-results).

## Using a debugger with Web Platform Tests

To attach a debugger to Servo while running a Web Platform Test, add the `--debugger` flag to your `./mach test-wpt` command.
There are two modes of operation:

1. When using the `servodriver` test harness (the default), you must run a command to attach your debugger in another terminal.
A sample command is provided in the output of the `./mach test-wpt` command; the test harness will then wait for 30 seconds before continuing execution.
2. When using the `servo` test harness (`--product=servo`), the debugger will automatically attach for you.
To continue the test harness execution, use `run` from the debugger prompt.
