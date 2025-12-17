# Architecture overview

The Servo project maintains a number of repositories that are either independent from Servo or forked from some upstream project with ongoing updates.

## Repositories that are used throughout the rust ecosystem

- [ipc-channel](https://github.com/servo/ipc-channel): Crate for the rust ecosystem of making IPC work.
- [string-cache](https://github.com/servo/string-cache): String interning library.
- [surfman](https://github.com/servo/surfman): Low-Level cross platform Rust library for managing graphic surfaces.

## Repositories that are forked from upstream projects

- [euclid](https://github.com/servo/euclid): Geometric types.
- [mozjs](https://github.com/servo/mozjs): Spidermonkey, servos JavaScriptEngine based on Spidermonkey with a small patchset.
- [rust-url](https://github.com/servo/rust-url): Url type.
- [rust-content-security-policy](https://github.com/servo/rust-content-security-policy): Parse and validate Content Security Policy.
- [stylo](https://github.com/servo/stylo): Servos CSS engine based on Firefox CSS engine.
- [unicode-bidi](https://github.com/servo/unicode-bidi): Unicode Bidirectional Algorithm implementation.
- [webrender](https://github.com/servo/webrender): A fork of Firefox's webrender with a small patchset.

## Repositories that are mainly used by servo

- [book](https://github.com/servo/book): This book!
- [ci-runners](https://github.com/servo/ci-runners): Various things for servo CI (Continuous Integration).
- [html5ever](https://github.com/servo/html5ever): HTML5 high-performance parser.
- [malloc_size_of](https://github.com/servo/malloc_size_of): Measure the runtime size of values.
- [media](https://github.com/servo/media): media backends and similar that servo uses.
- [servo](https://github.com/servo/servo)servo: The main browser.
- [wpt](https://github.com/servo/wpt): Servo's fork the the Web Platform Tests.
