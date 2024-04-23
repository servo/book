<!-- TODO: needs copyediting -->

# Debugging

There are a few ways to debug Servo.
`mach` supports a `--debug` flag that searches a suitable debugger for you and runs Servo with the appropriate arguments under it:

```
./mach run --debug test.html
```

You can also specify an alternative debugger using the `--debugger` flag:

```
./mach run --debugger=my-debugger test.html
```

You can also, of course, run directly your debugger on the Servo binary:

```
$ gdb --args ./target/debug/servo test.html
```

## Logging

Before starting the debugger right away, you might want to get some information about what's happening, how, and when.
Luckily, Servo comes with plenty of logs that will help us.
Type these 2 commands:

```shell
./mach run -d -- --help
./mach run -d -- --debug help
```

A typical command might be:

```shell
./mach run -d -- -i -y 1 --debug dump-style-tree /tmp/a.html
```

… to avoid using too many threads and make things easier to understand.

On macOS, you can add some Cocoa-specific debug options:

```shell
./mach run -d -- /tmp/a.html -- -NSShowAllViews YES
```

You can also enable some extra logging (warning: verbose!):

```
RUST_LOG="debug" ./mach run -d -- /tmp/a.html
```

Using `RUST_LOG="debug"` is usually the very first thing you might want to do if you have no idea what to look for.
Because this is very verbose, you can combine these with `ts` (`moreutils` package (apt-get, brew)) to add timestamps and `tee` to save the logs (while keeping them in the console):

```
RUST_LOG="debug" ./mach run -d -- -i -y 1 /tmp/a.html 2>&1 | ts -s "%.S: " | tee /tmp/log.txt
```

You can filter by crate or module, for example `RUST_LOG="layout::inline=debug" ./mach run …`.
Check the [env_logger](https://docs.rs/env_logger) documentation for more details.

Use `RUST_BACKTRACE=1` to dump the backtrace when Servo panics.

## println!()

You will want to add your own logs.
Luckily, many structures [implement the `fmt::Debug` trait](https://doc.rust-lang.org/std/fmt/#fmtdisplay-vs-fmtdebug), so adding:

```rust
println!("foobar: {:?}", foobar)
```

usually just works.
If it doesn't, maybe some of foobar's properties don't implement the right trait.

## Debugger

To run the debugger:

```shell
./mach run -d --debug -- -y 1 /tmp/a.html
```

This will start `lldb` on Mac, and `gdb` on Linux.

From here, use:

```shell
(lldb) b a_servo_function # add a breakpoint
(lldb) run # run until breakpoint is reached
(lldb) bt # see backtrace
(lldb) frame n # choose the stack frame from the number in the bt
(lldb) thread list
(lldb) next / step / …
(lldb) print varname
```

And to search for a function's full name/regex:

```shell
(lldb) image lookup -r -n <name> #lldb
(gdb) info functions <name> #gdb
```

See this [lldb tutorial](https://lldb.llvm.org/tutorial.html) and this [gdb tutorial](http://www.unknownroad.com/rtfm/gdbtut/gdbtoc.html).

To inspect variables and you are new with lldb, we recommend using the `gui` mode (use left/right to expand variables):

```
(lldb) gui
┌──<Variables>───────────────────────────────────────────────────────────────────────────┐
│ ◆─(&mut gfx::paint_task::PaintTask<Box<CompositorProxy>>) self = 0x000070000163a5b0    │
│ ├─◆─(msg::constellation_msg::PipelineId) id                                            │
│ ├─◆─(url::Url) _url                                                                    │
│ │ ├─◆─(collections::string::String) scheme                                             │
│ │ │ └─◆─(collections::vec::Vec<u8>) vec                                                │
│ │ ├─◆─(url::SchemeData) scheme_data                                                    │
│ │ ├─◆─(core::option::Option<collections::string::String>) query                        │
│ │ └─◆─(core::option::Option<collections::string::String>) fragment                     │
│ ├─◆─(std::sync::mpsc::Receiver<gfx::paint_task::LayoutToPaintMsg>) layout_to_paint_port│
│ ├─◆─(std::sync::mpsc::Receiver<gfx::paint_task::ChromeToPaintMsg>) chrome_to_paint_port│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

If lldb crashes on certain lines involving the `profile()` function, it's not just you.
Comment out the profiling code, and only keep the inner function, and that should do it.

## Debugging Servo with [rr][rr].

To record a trace under rr you can either use:

```
$ ./mach run --debugger=rr testcase.html
```

Or:

```
$ rr record ./target/debug/servo testcase.html
```

## Running WPT tests under rr's chaos mode.

Matt added a mode to Servo's testing commands to record traces of Servo running a test or set of tests until the result is unexpected.

To use this, you can pass the `--chaos` argument to `mach test-wpt`:

```
$ ./mach test-wpt --chaos path/to/test
```

Note that for this to work you need to have `rr` in your `PATH`.

Also, note that this might generate a lot of traces, so you might want to delete them when you're done.
They're under `$HOME/.local/share/rr`.

[rr]: http://rr-project.org/
