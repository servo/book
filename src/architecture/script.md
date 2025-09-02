<!-- TODO: needs copyediting -->

# Script

TODO:

- <https://github.com/servo/servo/blob/main/components/script/script_thread.rs>
- [JavaScript: Servo’s only garbage collector](https://research.mozilla.org/2014/08/26/javascript-servos-only-garbage-collector/)

## SpiderMonkey

Current state of, and outlook on, Servo's integration of SpiderMonkey: [https://github.com/gterzian/spidermonkey_servo](https://github.com/servo/servo/wiki/Servo-and-SpiderMonkey-Report)

## DOM Bindings

DOM bindings are implementation of webidl interfaces. The webidl interfaces are located `components/script_bindings/webidls/`; these define the interfaces names, their attributes, and their methods. The implementation of these interfaces is located in `components/script/dom/`. The implementation includes the actual data the object contains.

- [How to work on a Web API](web_api.md)

## Script Thread

- [Microtask queuing](microtasks.md)

## Layout DOM
