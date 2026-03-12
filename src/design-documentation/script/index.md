# Script

Servo is unique in that it uses garbage collection for some things that are non obvious. For example, every dom object
(a struct with `#[dom_struct])` on it is controlled by spidermonkeys garbage collector. Extra care is to be taken when interacting with this. Which is what this document is about. While the garbage collector is complicated and has multiple modes we will assume for now the following.
Whenever the GC runs, the rust program is stopped at whatever state it was in.
Servo is unique in that it uses garbage collection for some things that are non-obvious.
For example, every DOM object (a struct with `#[dom_struct])` is owned by SpiderMonkey's garbage collector.
This necessitates that the engine APIs that interact with these objects must be sound when garbage collection can occur at many points in the program.
While [the garbage collector](https://firefox-source-docs.mozilla.org/js/gc.html) is complex and has multiple modes, we can assume that whenever the GC runs then the Rust program does not run concurrently.

## Rooting and rooted types

An important part of garbage collection is establishing the roots of the object graph.
A root tells the garbage collector two things:
1. Do not delete any value that is transitively reachable from this root.
2. If garbage collection causes this rooted value to be moved in memory, all pointers to this value should be updated.

In Servo's code, roots are created automatically by using the `DomRoot<T>`, `Root<T>`, and `Rooted<T>` types.
See the [module documentation](https://doc.servo.org/script/dom/bindings/root/index.html) for more details.

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
and we would have invalid access when playing with them! This holds even if Kittens was rooted by some other mechanism earlier in the call chain.
If our data is not rooted correctly, the GC could pause our program after we got the reference to children, move the `kittens` value in memory, and we would have invalid access when playing with them!
This is true even if `kittens` was rooted by the code that called `play_with_kittens`.
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
Unrooting (the reverse) will automatically be done via a Drop impl on `DomRoot<T>`.

To ensure web API implementations in Servo are sound, the engine code is conservative and usually returns rooted types (such as `DomRoot<Node>`).
This is an acceptable tradeoff between safety and performance because rooting and unrooting operations are efficient.

## CanGC and Crown
Now rooting could be easily forgotten when implementing particular exciting apis. How to we prevent this?
Crown is the answer (if you are working on Script things you should run `./mach build --use-crown` to be sure it is checking things.
In essence, Crown just checks that you do not forgotten to root things and you will sometimes see certain lints in the code talking to crown such as `#[cfg_attr(crown, allow(crown::unrooted_must_root))]`. These essentially disable crown and should only be used in very specific circumstances.

But there is another piece of the puzzle. CanGC.
Some method interacting with the DOM will never have any chance of starting GC operations. So we can relax our requirement there.
As the name implies, if a function takes this argument it means that it can have a GC operation in the middle of it and crown needs to check it.

```rust
fn some_function(cats: &Kittens, can_gc: CanGc) {
    let children = Root::from_ref(cats.children);
    play_with_cats(children);
    cleanup_after_cats(children, can_gc);
}
```

The pecise notion of this is that we can be sure that no GC will happen when we call 'play_with_cats' but there
might be a GC happening while we call 'cleanup_after_cats'. The reason why some methods can incur GC and some methods do not are deep in the SpiderMonkey connections to servo and you will generally not be obvious.
In essence, you can not use can_gc until you call a method that needs it and then you go back along your callstack and give it as argument to every call until you arrive in something origininating from 'Bindings.conf' (see how to implement a dom meth'od).

You will sometimes see '&JSContext' and &mut JSContext' and 'NoGC'. You can think of '&mut JSContext' as a 'CanGc' and 'JSContext' and 'NoGC' as the absence of 'CanGc'.

JSContext and associates are the new way as they have some advantages.


# The performance of rooting

```rust
#[dom_struct]
struct Kittens {
    children: Vec<Cat>
}

fn some_function(cats: &Kittens) {
    let happy = cats.children.iter().map(|cat| Root::from_ref(cat)).any(|cat| cat.is_purring());
    if happy {
        println!("Happy cat found!");
    }
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
```

This API for interacting with kittens is safely rooted, but when there are many children the rooting and unrooting work can add up.

Yes. Remember rusts golden rule that &mut can only be hold exactly once!
What if we have a new type
```rust
struct UnrootedDom<'a> {
    inner_cat: Cat,
    js_context: &mut 'a JSContext,
}
```

Then whenever we have a handle on `UnrootedDom` we know that as long as this lives we can not call any methods that has a GC.
The following is **invalid** code.
```rust
#[dom_struct]
struct Kittens {
    children: Vec<UnrootedDom<'_>>,
}

fn make_cats(cx: &mut JSContext) -> Kittens {}

fn play_with_cat(cx: &JSContext, cat: Cat) {}

fn cleanup_after_cats(cx: &mut JSContext, cat: Cat) {}

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

## Further information
Now that you understand the basics of read only access, there is more to learn on using writeable Dom Objects [[borrow_hazard.md]].


## More Information
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
