# Architecture overview

The servo browser owns a couple of crates that are either mostly independent or based on some upstream project. This gives a list of them.
We highlight crates with **crate** for crates that are used throughout the rust ecosystem and _crate_ for crates used in Firefox work.
You should use a bit more care before changing them.

- servo: The main browser
- _mozjs_: Spidermonkey, servos JavaScriptEngine based on Spidermonkey with a small patchset.
- ci-runners: Various things for servo CI (Continuous Integration).
- wpt: Servo's fork the the Web Platform Tests
- _stylo_: Servos CSS engine based on Firefox CSS engine.
- html5ever: HTML5 high-performance parser.
- media: media backends and similar that servo uses.
- book: This book!
- _webrender_: A fork of Firefox's webrender with a small patchset
- **Ipc-channel**: Crate for the rust ecosystem of making IPC work.
- **Surfman**: Low-Level cross platform Rust library for managing graphic surfaces.
- **unicode-bidi**: Unicode Bidirectional Algorithm implementation.
- rust-content-security-policy: Content Security Policy crate.
- **string-cachen**: String interning library.
- **MallocSizeOf**: Measuring the runtime size of a value to use memory calculation.
- **Euclid**: Geometric types.
- **Pathfinder**: GPU-based rasterizer for fonts and vector graphics.
