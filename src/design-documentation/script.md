# Script

Servo is unique in that it uses garbage collection for some things that are non obvious. For example, every dom object
(a struct with `#[dom_struct])` on it is controlled by spidermonkeys garbage collector. Extra care is to be taken when interacting with this. While the garbage collector is complicated and has multiple modes we will assume for now the following.
Whenever the GC runs, the rust program is stopped at whatever state it was in.

## Rooting and you

The most often used method is Rooting. Rooting (`Root<Dom<T>>`) means that we tell the garbage collector two things.
- Please do not delete any value that is reachable by this root.
- Please fix any pointer that points to this after you do a garbage collection.

In the following we will look at some code that is close to what is happening behind some abstractions but not the complete picture.
Let us now assume we have the following code:
```rust
#[dom_struct]
struct Kittens {
    children: Vec<Dom<Cat>>
}

fn some_function(cats: &Kittens) {
    let children = & cats.children;
    play_with(children)
}
```

Without rooting the GC could pause our program after we got the reference to children, move the `Kittens` struct around
and we would have invalid access when playing with them! This holds even if Kittens was rooted by some other mechanism earlier in the call chain.
Hence, we need to transform the code into
```rust
#[dom_struct]
struct Kittens {
    children: Vec<Dom<Cat>>
}

fn some_function(cats: &Kittens) {
    let children: DomRoot<Vec<Dom<Cat>>> = cats.children().iter().map(|cat| cat.as_rooted()).collect();
    play_with(children)
}
```
Unrooting (the reverse) will automatically be done via a Drop impl on Root.

When you implement some HTML api you will generally only encounter rooted things (such as 'DomRoot\<Node\>'). And rooting
and unrooting is generally pretty fast.

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
}
```

Now if the litter is especially large, we do a lot of work just rooting and unrooting the cats only to test a probably fast bool. Can we do something about this?

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
