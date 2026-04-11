# DOM Bindings

The DOM bindings are implementations of [WebIDL](https://en.wikipedia.org/wiki/Web_IDL) interfaces in native Rust code.
A code generator is responsible for producing glue code that exposes these native Rust implementations to JavaScript via the SpiderMonkey API.
The WebIDL files themselves are located in `components/script_bindings/webidls/`.
These files contain the definition of each interface including their names, attributes, and methods.
The Rust implementations of these interfaces are contained in `components/script/dom`.
Each Rust implementation is a special Rust `struct` which holds the state of each DOM object.


## Layout Wrappers

JavaScript runs in a single thread and the DOM interfaces are not thread-safe.
Layout needs to access the DOM, but is expected to run across different threads.
In theory, this can work as long as a thread does not try to read from or mutate a DOM object while another thread is mutating the same object.
We try to make this bit of unsafety easier to manage by limiting how layout can use DOM objects via a wrapper `struct` that exposes a limited, yet compatible, set of functionality.

There are two usage patterns:

1. Layout itself assumes that only a single thread "owns" the DOM wrapper for each node and thus writing to the DOM should be safe.
   Children of the node may be processed in other threads concurrently.
   On the other hand, accessing the parent is highly unsafe, as another thread may be writing to and reading from the parent node.
2. `stylo` and `selectors` assume that nodes can be accessed from any thread, but only a single thread will write to a node at once.
   This means that accessing parents and children is safe, but writing to the node is highly unsafe.

In addition, `layout` depends on the `script`, so it is not possible to pass DOM instances directly from `script` to `layout` otherwise we would have a dependency cycle.
Instead `layout-api` exposes a trait-based interface and `script` implements it.
This allows the `Layout` interface to deal with nodes directly.

The four traits that we expose are:

 - `LayoutNode`: This is the basic interface for a DOM node that is used for layout.
 - `DangerousStyleNode`: This is the interface which implements `stylo` and `selectors` traits for interacting with nodes.
    This can be created from a `LayoutNode` by calling the unsafe method `LayoutNode::dangerous_style_node()`.
    In general, these nodes should not be used by layout code, unless passing them directly to a `stylo` or `selectors` call.
 - `LayoutElement`: This is the basic interface for a DOM element that is used for layout.
 - `DangerousStyleElement`: This is the interface which implements `stylo` and `selectors` traits for interacting with elements.
    This can be created from a `LayoutElement` by calling the unsafe method `LayoutElement::dangerous_style_element()`.
    In general, these elements should not be used by layout code, unless passing them directly to a `stylo` or `selectors` call.

`script` implements these traits with `ServoLayoutNode`, `ServoDangerousStyleNode`, `ServoLayoutElement`, and `ServoDangerousLayoutElement`.
In addition, `script` exposes two other structs which implement `stylo` traits: `ServoDangerousStyleDocument` and `ServoDangerousStyleShadowRoot`.

### Rules for Layout Wrappers

 - In order to keep things simple and build times faster, the trait definitions (`LayoutNode` and `LayoutElement`) should not contain any default methods.
   All implementation code should be in `script`.
 - Layout *should not* use `DangerousStyleNode` and `DangerousStyleElement` unless calling into `stylo` or `selectors`.
   There are currently a few exceptions, but they will be eliminated gradually.
 - Layout should not rely on methods defined only on `ServoLayoutNode` and `ServoLayoutElement`.
   Instead, new functionality should be added to the `LayoutNode` or `LayoutElement` traits and then implemented in `ServoLayoutNode` or `ServoLayoutElement`.
   This will allow eliminating `TrustedNodeAddress` in the future and passing `LayoutNode`s directly to layout, removing a source of unsafe code.
