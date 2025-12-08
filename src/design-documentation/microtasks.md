<!-- TODO: needs copyediting -->

# Microtasks

According the HTML spec, a microtask is: "a colloquial way of referring to a task that was created via the queue a microtask algorithm"([source](https://html.spec.whatwg.org/multipage/#microtask-queue)).
Each [event-loop](https://html.spec.whatwg.org/multipage/webappapis.html#event-loop)--meaning window, worker, or worklet--has its own microtask queue.
The tasks queued on it are run as part of the [perform a microtask checkpoint](https://html.spec.whatwg.org/multipage/#perform-a-microtask-checkpoint) algorithm, which is called into from various places, the main one being [after running a task](https://html.spec.whatwg.org/multipage/#event-loop-processing-model:perform-a-microtask-checkpoint) from a task queue that isn't the microtask queue, and each call to this algorithm drains the microtask queue--running all tasks that have been enqueued up to that point([without re-entrancy](https://html.spec.whatwg.org/multipage/#performing-a-microtask-checkpoint)).

## The microtask queue in Servo

The [`MicroTaskQueue`](https://github.com/servo/servo/blob/4357751f285c79bf37a8e7a02d4c8dc4f7a8ae69/components/script/microtask.rs#L31) is a straightforward implementation based on the spec: a list of tasks and a boolean to prevent re-entrancy at the checkpoint.
One is [created for each runtime](https://github.com/servo/servo/blob/4357751f285c79bf37a8e7a02d4c8dc4f7a8ae69/components/script/script_runtime.rs#L519), matching the spec since a runtime is [created per event-loop](https://github.com/servo/servo/blob/4357751f285c79bf37a8e7a02d4c8dc4f7a8ae69/components/script/script_runtime.rs#L445).
For a window event-loop, which can [contain multiple window objects](https://html.spec.whatwg.org/multipage/#similar-origin-window-agent), the queue is [shared among all `GlobalScope`](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/globalscope.rs#L278) it contains.
Dedicated workers [use a child runtime](https://github.com/servo/servo/blob/4357751f285c79bf37a8e7a02d4c8dc4f7a8ae69/components/script/dom/dedicatedworkerglobalscope.rs#L384), but that one still comes with its own microtask queue.


### Microtask queueing
A task can be enqueued on the microtask queue from both Rust, and from the JS engine.

- From JS: the JS engine will call into [`enqueue_promise_job`](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/script_runtime.rs#L196) whenever it needs to queue a microtask to call into promise handlers.
  This callback mechanism is set up [once per runtime](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/script_runtime.rs#L520).
  This means that resolving a promise, either [from Rust](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/promise.rs#L173) or from JS, will result in this callback being called into, and a microtask being enqueued.
  Strictly speaking, the microtask is [still enqueued from Rust](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/script_runtime.rs#L222).
- From Rust, there are various places from which microtask are explicitly enqueued by "native" Rust:
  - To implement the [await a stable state](https://html.spec.whatwg.org/multipage/#await-a-stable-state) algorithm, via the [script-thread](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/script_thread.rs#L966), apparently only via the script-thread, meaning worker event-loop never use this algorithm.
  - To implement the [dom-queuemicrotask](https://html.spec.whatwg.org/multipage/#dom-queuemicrotask) algorithm, both on [window](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/window.rs#L928) and [worker](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/workerglobalscope.rs#L384) event-loops.
  - And various other places in the DOM, which can all be traced back to the variants of [`Microtask`](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/microtask.rs#L39)
  - A microtask can only ever be enqueued from steps running on a task itself, never from steps running "in-parallel" to an event-loop.

### Running Microtask Checkpoints
The [perform-a-microtask-checkpoint](https://html.spec.whatwg.org/multipage/#perform-a-microtask-checkpoint) corresponds to [`MicrotaskQueue::checkpoint`](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/microtask.rs#L85), and is called into at multiple points:
- In the parser, when [encountering a `script` tag](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/servoparser/mod.rs#L621) as part of tokenizing.
  This corresponds to [#parsing-main-incdata:perform-a-microtask-checkpoint](https://html.spec.whatwg.org/multipage/#parsing-main-incdata:perform-a-microtask-checkpoint).
- Again in the parser, ss part of [creating an element](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/servoparser/mod.rs#L1332).
  This corresponds to [#creating-and-inserting-nodes:perform-a-microtask-checkpoint](https://html.spec.whatwg.org/multipage/#creating-and-inserting-nodes:perform-a-microtask-checkpoint).
- As part of [cleaning-up after running a script](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/bindings/settings_stack.rs#L79).
  This corresponds to [#calling-scripts:perform-a-microtask-checkpoint](https://html.spec.whatwg.org/multipage/#calling-scripts:perform-a-microtask-checkpoint).
- At two points([one](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/customelementregistry.rs#L730), [two](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/customelementregistry.rs#L921)) in the `CustomElementRegistry`, the spec origin of these calls is unclear: it appears to be "clean-up after script", but there are no reference to this in the parts of the spec that the methods are documented with.
- In a [worker event-loop](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/abstractworkerglobalscope.rs#L158), as part of step 2.8 of the [event-loop-processing-model](https://html.spec.whatwg.org/multipage/#event-loop-processing-model)
- In two places([one](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/script_thread.rs#L1882), [two](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/script_thread.rs#L1973)) in a window event-loop(the `ScriptThread`), again as part of step 2.8 of the [event-loop-processing-model](https://html.spec.whatwg.org/multipage/#event-loop-processing-model).
  This needs to consolidated into one call, and what is a "task" needs to be clarified([TODO(#32003)](https://github.com/servo/servo/issues/32003)).
- Our [paint worklet implementation](https://github.com/servo/servo/blob/7eac599aa1d6bcf8858c51d90763373f0dd5f289/components/script/dom/paintworkletglobalscope.rs) does not seem to run this algorithm yet.
