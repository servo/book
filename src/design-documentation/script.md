<!-- TODO: needs copyediting -->

# Script

TODO:

- <https://github.com/servo/servo/blob/main/components/script/script_thread.rs>
- [JavaScript: Servo’s only garbage collector](https://research.mozilla.org/2014/08/26/javascript-servos-only-garbage-collector/)

## SpiderMonkey

Current state of, and outlook on, Servo's integration of SpiderMonkey: [https://github.com/gterzian/spidermonkey_servo](https://github.com/servo/servo/wiki/Servo-and-SpiderMonkey-Report)

## DOM Bindings

DOM bindings are implementations of WebIDL interfaces.
The WebIDL interfaces are located in `components/script_bindings/webidls/`; these define the interfaces names, their attributes, and their methods.
The implementation of these interfaces is located in `components/script/dom/`.
The implementation includes the actual data the object contains.

- [How to work on a Web API](../guides/implementing-a-dom-api.md)

## Script Thread

- [Microtask queuing](microtasks.md)

## Layout DOM
