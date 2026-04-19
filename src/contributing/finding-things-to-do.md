# Finding Things to Do

Servo's [issue tracker](https://github.com/servo/servo/issues/) contains a lot of issues, and it can feel overwhelming looking for something to work on.
Here are some helpful tips for issue labels to look for:

## Less complex issues

The [E-less-complex](https://github.com/servo/servo/issues/?q=is%3Aissue%20state%3Aopen%20label%3AE-less-complex) label means that someone thinks the issue is appropriate for a new contributor.
Issues with this label should contain a clear description of the problem, clear steps to follow to address it, and any expected verification steps.

## More complex issues

The [E-more-complex](https://github.com/servo/servo/issues/?q=is%3Aissue%20state%3Aopen%20label%3AE-more-complex) label means that someone thinks ths issue is appropriate for someone with a bit of experience.
Like `E-less-complex`, issues with this label should contain a clear description of the problem, clear steps to follow to address it, and any expected verification steps.
The difference between the two labels is the expected effort required to solve it, and they may require additional investigation to solve.

## Fixing panics with minimized testcases

There are many ways to make Servo panic, and often these are found by [fuzzing](https://en.wikipedia.org/wiki/Fuzzing) Servo.
There are lots of examples of issues with minimized testcases (i.e. the smallest HTML/JS/CSS required to reproduce a problem) that are labelled with [I-panic and C-has-manual-testcase](https://github.com/servo/servo/issues/?q=is%3Aissue%20state%3Aopen%20label%3AI-panic%20label%3AC-has-manual-testcase).

These can be good issues to work on because the panic backtrace can provide pointers to relevant code, and you can focus on understanding the conditions that trigger the panic.

## Minimizing testcases

It's easy to file an issue about Servo rendering a web page incorrectly, but it's often difficult to act on those issues.
It's very helpful to look for issues with the [`C-needs minimized testcase` label](https://github.com/servo/servo/issues/?q=is%3Aissue%20state%3Aopen%20label%3A%22C-needs%20minimized%20testcase%22) and work on isolating the HTML/CSS/JS required to reproduce the problem.
See the [guide](guides/minimal-reproducible-test-cases.md) for tips about minimizing nontrivial pages.

## Diagnosing failing Web Platform Tests

The [Web Platform Tests](https://web-platform-tests.org/) (WPT) are Servo's main source of automated conformance tests.
There are many tests that Servo does not yet pass, and these can be found by looking at the [test metadata directory](https://github.com/servo/servo/tree/main/tests/wpt/meta).
Every `.ini`. file under that directory corresponds to a [test source file](https://github.com/servo/servo/tree/main/tests/wpt/tests), and it can be helpful to choose a file in directory that interests you and diagnose what is causing the test not to pass.

You can also explore all the tests that Servo fails in the web-based [wpt.fyi interface](https://wpt.fyi/results/?label=master&label=experimental&product=servo&aligned).
See the [guide](guides/diagnosing-errors/stable-wpt-errors.md) for tips about identifying the cause of WPT test failures.
