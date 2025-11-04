# Garbage collection and RefCell

There is a subtle interaction between Servo's integration with SpiderMonkey's garbage collector and Rust's model for shared ownership.
Since DOM objects in Servo are not uniquely owned, we must use `RefCell`/`DomRefCell` for members that can be mutated.
When a garbage collection (GC) operation is triggered from SpiderMonkey, every DOM object is traced to find any reachable JS value.
This tracing is implemented by the `JSTraceable` derive, which calls `JSTraceable::trace` on each member of the DOM object (unless it is annotated with `#[no_trace]`).
Since the `JSTraceable` implementation for `RefCell` borrows the cell, this means that any mutable borrow of a DOM object's member will trigger a panic if a GC occurs while the borrow is still active.
We often refer to this in Servo as a **borrow hazard**.

## Recognizing borrow hazards: `CanGc`

Servo has a type named [`CanGc`](https://github.com/servo/servo/blob/9fa6303d261f2aca3a19448fefda69280c4d8892/components/script_bindings/script_runtime.rs#L48-L62) which is used to indicate when a GC could occur before the callee returns.
There is one rule: when calling a function that accepts a `CanGc` argument, the caller must also accept a `CanGc` argument.

There are exceptions to this rule:
* trait methods that are defined outside of the `script`/`script_bindings` crates cannot propagate `CanGc`, so implementations must use `CanGc::note()` if a `CanGc` argument is required by a callee 
* async tasks must use `CanGc::note()`, since they execute independently of the caller's stack frame
* `extern "C"` functions must use `CanGc::note()`, since they require a matching signature for some external library

When `CanGc` is propagated correctly through a piece of code, borrow hazards can be identified by looking for uses of `borrow_mut()` nearby uses of `can_gc`.
In particular, when the return value of `borrow_mut()` is stored in a variable, and that variable is still alive when a function call includes a `can_gc` argument, there's a very good chance that it's a panic waiting to be triggered!

See an [example issue](https://github.com/servo/servo/issues/39947) highlighting a borrow hazard.
To learn more, see the [original issue](https://github.com/servo/servo/issues/33140) proposing a static analysis.

## Verifying borrow hazards

To verify that a particular mutable borrow can trigger be triggered when a GC occurs, we need 1) deterministic garbage collection, 2) a way to run the suspicious code.
To make garbage collection deterministic, you first need to build Servo with `--debug-mozjs`, then run it with `--pref js_mem_gc_zeal_level=2 --pref js_mem_gc_zeal_frequency=1`.
This enables a mode where the garbage collector runs any time a JS allocation occurs, and is guaranteed to trigger any latent borrow hazards.
It is also very slow, so minimizing your testcase will save you time.
If you are unsure of exactly how to trigger the suspicious code, add a panic to it and run WPT tests from the appropriate directory until you find a test file that panics.

## Patterns for fixing borrow hazards

* Force the borrow to be dropped earlier by scoping it (`{ ... }`)
* Clone a temporary value out of the borrowed value so the borrow can be dropped earlier
* Instead of `RefCell<SomeStruct>`, make members inside of `SomeStruct` use `RefCell`/`Cell`
* Split a mixed immutable/mutable borrow into multiple scoped immutable borrows and only use mutable borrows when the mutation occurs

## Examples of fixing borrow hazards

* https://github.com/servo/servo/pull/40139
* https://github.com/servo/servo/pull/40138

## Examples of propagating CanGc arguments

* https://github.com/servo/servo/pull/40033
* https://github.com/servo/servo/pull/36180
* https://github.com/servo/servo/pull/40325

## Adding `CanGc` arguments to generated DOM method traits

The extra arguments to WebIDL methods are controlled by the [`Bindings.conf`](https://github.com/servo/servo/blob/main/components/script_bindings/codegen/Bindings.conf) file.
`CanGc` arguments in particular are controlled by the `canGc` key for a particular interface.
If an interface is not yet listed in the file, feel free to add it.
