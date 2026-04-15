# Script
This document should get you up to speed on Script Thread, rooting and Gc. It is by no means complete.

Servo is unique in that it uses garbage collection for some things that are non-obvious.
For example, every DOM object (a struct with `#[dom_struct]`) is owned by SpiderMonkey's garbage collector.
This necessitates that the engine APIs that interact with these objects must be sound when garbage collection can occur at many points in the program.
While [the garbage collector](https://firefox-source-docs.mozilla.org/js/gc.html) (GC) is complex and has multiple modes, we can assume that whenever the GC runs then the Rust program does not run.

## Rooting and rooted types

An important part of garbage collection is establishing the roots of the object graph.
A root tells the garbage collector two things:
1. Do not delete any value that is transitively reachable from this root.
2. If garbage collection causes this rooted value to be moved in memory, all pointers to this value should be updated.

In Servo's code, roots are created automatically by using the `DomRoot<T>`, `Root<T>`, and `Rooted<T>` types.
See the [module documentation](https://doc.servo.org/script/dom/bindings/root/index.html) for more details about the difference. These types implement `Deref`, so we can treat them as
normal references.

The following examples contain simplifications of real Servo code patterns to make them easier to understand.
Assume the following code, declaring a `Kittens` type that contains pointers to `Cat` types, all of which are owned by the garbage collector:
```rust
#[dom_struct]
struct Kittens {
    children: Vec<Dom<Cat>>
}

fn play_with_kittens(kittens: &Kittens) {
    let children = & cats.children;
    play_with(children)
}
```

Without rooting the GC could pause our program after we got the reference to children, move the `Kittens` struct around
and we would have invalid access when playing with them!
This holds even if Kittens was rooted by some other mechanism earlier in the call chain.
Remember that the Garbage Collector cannot change pointers of our local variable 'children' if it doesn't know about it.

Hence, we need to transform the code into
```rust
#[dom_struct]
struct Kittens {
    children: Vec<Dom<Cat>>
}

fn play_with_kittens(cats: &Kittens) {
    let children: Vec<DomRoot<Cat>> = cats.children.iter().map(|cat| cat.as_rooted()).collect();
    play_with(children)
}
```
We will assume that getting the cat reference and rooting it is one atomic action.
Unrooting (the reverse) will automatically be done via a Drop impl on `DomRoot<T>`.

To ensure web API implementations in Servo are sound, the engine code is conservative and usually returns rooted types (such as `DomRoot<Node>`).
This is an acceptable tradeoff between safety and performance because rooting and unrooting operations are efficient; they essentially just push and pop vector elements.

## Crown and CanGc
It's easy to overlook rooting concerns when implementing new APIs.
Crown is the answer (if you are working on Script things you should run `./mach build --use-crown` to be sure it is checking things).
In essence, Crown just checks that you do not forgotten to root things and you will sometimes see certain lints in the code talking to crown such as `#[cfg_attr(crown, allow(crown::unrooted_must_root))]`. These essentially disable crown and should only be used in very specific circumstances.

But there is another piece of the puzzle tangentially related. While rooting gives us the way to enforce the GC to play nice with our rust pointers, we also have rust RefCells. While the pointers for these are now properly handled by the GC, the GC needs to borrow the `RefCell` to test reachability and redirect the pointer.
But we can only borrow a `RefCell` not simulataneously. What happens if we have a Gc pause while having a cell borrowd?

```rust
struct CatCarrier {
    cat: RefCell<Dom<Cat>>,
}

fn some_function(carrier: &CatCarrier) {
    let mutable_cat = carrier.inner_cat.borrow_mut().as_rooted();
    play_with_cat_mutably(mutable_cat);
    cleanup_playspace();
}
```
Now assume that `cleanup_playspace` can call the GC. It could then happen that we
- Hold the mutable borrow to the cat inside the carrier.
- Cleanup after the cat.
- The GC pauses and tries to trace the rooted `mutable_cat` via borrowing the RefCell.
- Panics because the RefCell can only be borrowed mutably once!

We call this a borrow hazard. To prevent this we have the following solution.

```rust
fn some_function(carrier: &CatCarrier, can_gc: CanGc) {
    {
        let mutable_cat = carrier.inner_cat.borrow_mut().as_rooted();
        play_with_cat_mutably(mutable_cat);
    }
    cleanup_playspace(can_gc);
}
```

Now this example is not complete and only here to illustrate the following point.
CanGC (which is a trivial type and easily copyable) was introduced, not as a
formal prevention of the borrow hazard but as a note to the programmer. It says:
Be careful if you want to have a mutable borrow that it does not cross the boundaries
of a function taking `CanGc`.

There are more details [here](borrow_hazard.md) on how to recognize and handle borrow hazards.
We only want to use this as a motivating example for the following section on `&JSContext`
and `&mut JSContext`.

Our running example would then look something like this:

```rust
fn some_function(cats: &Kittens, can_gc: CanGc) {
    let children: Vec<DomRoot<Cat>> = cats.children.iter().map(|cat| cat.as_rooted()).collect();
    play_with_cats(children);
    cleanup_after_cats(children, can_gc);
}
```
The pecise notion of this is that we can be sure that no GC will happen when we call `play_with_cats` but there
might be a GC happening while we call `cleanup_after_cats`. The reason why some methods can incur GC and some methods do not are deep in the SpiderMonkey connections to servo and you will generally not be obvious.

What does it mean for you?
In essence, if a method you are calling needs `CanGc` you should have your method use `CanGc`
so that everybody can remember to be careful about borrow hazards around the code.


# JSContext, &mut JSContext
But as you can see this can be hazardous. What if somebody forgot to use the `CanGc` attribute
in their function call but actually does call the GC somewhere deep in the call stack?
Then we created a borrow hazard that will lead to crashes we might not understand.
To solve this we introduce `JSContext` and `&mut JSContext`.
Unlike `CanGc`, these types use the Rust compiler's borrowing rules and SpiderMonkey API wrappers to ensure that any API that can trigger garbage collection requires a `&mut JSContext` argument.
Since these values are unique, they must be passed by callers.
Similarly, any API function that _cannot_ GC but still requires access to a JS context only takes a `&JSContext` argument.

There is also a `NoGc` type that can be constructed from a `JSContext`.
Since this type borrows the `&mut JSContext`, it makes it impossible to invoke any code that requires a `&mut JSContext` argument (i.e. can trigger a GC operation) while the `NoGc` value exists.

> Note:
> Currently the Servo codebase is transforming from the previous `CanGc` approach
> to the `JSContext` approach.
> You might see both in the codebase and also several escape hatches.


# The performance of rooting

```rust
#[dom_struct]
struct Kittens {
    children: Vec<Cat>
}

impl Kittens {
    fn children(&self) -> Vec<DomRoot<Cat>> {
        self.children.iter().map(|cat| cat.as_rooted()).collect()
    }
}

fn some_function(cats: &Kittens) {
    let happy = cats.children().iter().any(|cat| cat.is_purring());
    if happy {
        println!("Happy cat found!");
    }
}
```

This API for interacting with kittens is safely rooted, but when there are many children the rooting and unrooting work can add up.
We can use the `JSContext` types to ensure code that violates rooting rules won't trigger any GC operations that could observe those violations.

Since `&mut` is a unique borrow, we can introduce a new type:
```rust
struct UnrootedDom<'a, T> {
    inner_cat: Dom<T>,
    js_context: &mut 'a JSContext,
}
```

Then whenever we have a handle on `UnrootedDom` we know that as long as this lives we can not call any methods that has a GC.
The following is **invalid** code.
```rust
#[dom_struct]
struct Kittens {
    children: Vec<UnrootedDom<'_, Cat>>,
}

fn make_cats(cx: &mut JSContext) -> Kittens {}

fn play_with_cat(cx: &JSContext, cat: &Cat) {}

fn cleanup_after_cats(cx: &mut JSContext, cat: &Cat) {}

fn some_function(cx: &mut JSContext) {
    let cats = make_cats(cx);
    for cat in cats.children {
        play_with_cat(cx, cat.inner_cat)
    }
    for cat in cats.children {
        cleanup_after_cats(cx, cat)
    }
}
```

We will get a compile error that cx is borrowed mutably once by 'make_cats' and once by 'cleanup_after_cats'.
But notice that the call to 'play_with_cat' is perfectly fine.

This is the essence of 'UnrootedDomNode' and similar 'Unrooted' methods. Some of these might also take the 'NoGC' argument
```rust
fn play_with_cats<'a>(no_gc: &'a NoGC, cat: Cat) {}

fn some_function(cx: &mut JSContext, cat: &Cat) {
    play_with_cats(cx.no_gc(), cat);
}
```


## More Information
TODO:

- <https://github.com/servo/servo/blob/main/components/script/script_thread.rs>
- [JavaScript: Servo’s only garbage collector](https://research.mozilla.org/2014/08/26/javascript-servos-only-garbage-collector/)

## SpiderMonkey

Current state of, and outlook on, Servo's integration of SpiderMonkey: [https://github.com/gterzian/spidermonkey_servo](https://github.com/servo/servo/wiki/Servo-and-SpiderMonkey-Report)

- [How to work on a Web API](../guides/implementing-a-dom-api.md)

## Script Thread

- [Microtask queuing](microtasks.md)
