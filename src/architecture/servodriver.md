# The Servodriver test harness

Servodriver is a test harness built on top of the wptrunner framework and a WebDriver server.
It is not yet enabled by default, but can be run with the `--product servodriver` argument appended to any `test-wpt` command.
Servodriver is made of three main components: the web server inside Servo that implements the [WebDriver specification](https://www.w3.org/TR/webdriver2/), the Python test harness that orchestrates the browser, and the scripts that are loaded inside the test pages.

## The wptrunner harness

Wptrunner is the harness that uses an `executor` and `browser` combination to launch a supported product.
The [browser](https://github.com/servo/servo/blob/main/tests/wpt/tests/tools/wptrunner/wptrunner/browsers/servodriver.py) defines Python classes to instantiate and methods to invoke for supported configurations, as well as arguments to pass to the Servo binary when launching it.
It delegates all webdriver-specific logic to the base [WebDriverBrowser class](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/browsers/base.py#L294) that is common to all browsers that rely on WebDriver.

The Servodriver [executor](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/executorservodriver.py) defines Servo-specific test initialization/result processing and inter-test state management.
For example, Servo defines [WebDriver extension methods](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/executorservodriver.py#L23-L42) for managing preferences, and these are [invoked](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/executorservodriver.py#L88-L92) in between tests to ensure that each test runs with our [intended](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/meta/webxr/__dir__.ini#L1) configuration.

Our Servodriver executor delegates a lot of logic to the common [WebDriverTestharnessExecutor](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/executorwebdriver.py#L948).
This executor is responsible for executing scripts that ensure that the [testdriver harness executes](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/executorwebdriver.py#L840) and that the python harness is able to retrieve test results from the browser.

## Servo’s WebDriver implementation

There are three main components to this implementation: the server handler, the script handler, and the input handler.

### Server handler

When wptrunner connects to the [webdriver server](https://github.com/servo/servo/tree/3421185737deefe27e51e104708b02d9b3d4f4f3/components/webdriver_server/) in the new Servo instance, it creates a new [session](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/webdriver_server/lib.rs#L132).
This session persists state between webdriver API calls.
All API calls that interact with the browser are routed through the constellation as [ConstellationMsg::WebDriverCommand](https://doc.servo.org/script_traits/enum.WebDriverCommandMsg.html).
Any API call that needs to interact directly with content inside a document is part of the [WebDriverScriptCommand](https://doc.servo.org/script_traits/webdriver_msg/enum.WebDriverScriptCommand.html) enum.
Many of these APIs require a synchronous response and include an `IpcSender` channel that Servo’s webdriver server will use to [wait for a response](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/webdriver_server/lib.rs#L911).
However, cases like navigation and executing async scripts have additional synchronization:

#### Navigation

When a navigation is requested, the [constellation receives an IpcSender](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/webdriver_server/lib.rs#L677) that it stores.
When a navigation completes, the constellation [checks if the pipeline matches](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/constellation/constellation.rs#L3676) the navigation from webdriver and notifies the webdriver server using the original channel.

#### Async scripts

When an async script execution is initiated, the webdriver specification [provides a way](https://www.w3.org/TR/webdriver2/#execute-async-script) for scripts to communicate a result to the server.
The script is invoked as an [anonymous function](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/webdriver_server/lib.rs#L1532) with an [additional function argument](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/webdriver_server/lib.rs#L1524) that sends the response to the server.

### Script handler

When a webdriver message is received that targets a specific browsing context, it is [handled](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/script/script_thread.rs#L2076) by the ScriptThread that contains that document.
The logic for processing each command lives in [webdriver_handlers.rs](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/script/webdriver_handlers.rs).
Any command that returns a value derived from web content must [serialize JS values](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/script/webdriver_handlers.rs#L162) as values that the webdriver server can convert into [API value types](https://doc.servo.org/serde_json/value/enum.Value.html).

We expose [two web-accessible methods](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/script/dom/window.rs#L1189-L1203) for communicating async results to the WebDriver server: `Window.webdriverCallback` and `Window.webdriverTimeout`.

### Input handler

When the webdriver server receives input action commands (eg. pointer or mouse inputs), it creates an action sequence and [dispatches them progressively](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/webdriver_server/actions.rs#L110) to the compositor ([via the constellation](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/constellation/constellation.rs#L4548-L4559)).
The compositor then [handles these events](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/components/compositing/compositor.rs#L587-L601) the same as any input events received from the embedder (modulo [known bugs](https://github.com/servo/servo/issues/35394)).

## The test page scripts

The testdriver harness works by incorporating all of these elements together.
The executor [opens a new window](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/executorwebdriver.py#L850) and invokes an async script that [sets the testdriver callback](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/testharness_webdriver_resume.js) to `Window.webdriverCallback` (`arguments[arguments.length - 1]`).
This window creates [a message queue](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/message-queue.js#L30), which is [read by the executor harness](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/executors/executorwebdriver.py#L904-L905).
Subsequently, each test that runs is opened as a new window; these windows can then use `opener.postMessage` to communicate with the original window, which allows the testdriver APIs to send messages that [represent WebDriver API calls](https://github.com/servo/servo/blob/3421185737deefe27e51e104708b02d9b3d4f4f3/tests/wpt/tests/tools/wptrunner/wptrunner/testdriver-extra.js#L286-L296).

## Debugging hints

Always start with the following RUST_LOG:

```
RUST_LOG=webdriver_server,webdriver,script::webdriver_handlers,constellation
```

This usually makes it clear if the expected API calls are being processed.

When debugging input-related problems, add JS debugging lines that log the `getBoundingClientRect()` of whatever element is being clicked, then compare the coordinates received by the compositor when clicking manually vs the coordinates received from the WebDriver server.
