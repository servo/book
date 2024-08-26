# Debugging

One of the simplest ways to debug Servo is to print interesting variables with the [`println!`](https://doc.rust-lang.org/std/macro.println.html), [`eprintln!`](https://doc.rust-lang.org/std/macro.eprintln.html), or [`dbg!`](https://doc.rust-lang.org/std/macro.dbg.html) macros.
In general, these should only be used temporarily; you’ll need to remove them or convert them to proper debug logging before your pull request will be merged.

## Debug logging with `log` and `RUST_LOG`

Servo uses the [`log`](https://crates.io/crates/log) crate for long-term debug logging and error messages:

```rust
log::error!("hello");
log::warn!("hello");
log::info!("hello");
log::debug!("hello");
log::trace!("hello");
```

Unlike macros like `println!`, `log` adds a timestamp and tells you where the message came from:

```
[2024-05-01T09:07:42Z ERROR servoshell::app] hello
[2024-05-01T09:07:42Z WARN  servoshell::app] hello
[2024-05-01T09:07:42Z INFO  servoshell::app] hello
[2024-05-01T09:07:42Z DEBUG servoshell::app] hello
[2024-05-01T09:07:42Z TRACE servoshell::app] hello
```

You can use `RUST_LOG` to filter the output of `log` by level (`off`, `error`, `warn`, `info`, `debug`, `trace`) and/or by where the message came from, also known as the “target”.
Usually the target is a Rust module path like `servoshell::app`, but there are some special targets too (see [§ *Event tracing*](#event-tracing)).
To set `RUST_LOG`, prepend it to your command or use `export`:

```sh
$ RUST_LOG=warn ./mach run -d test.html     # Uses the prepended RUST_LOG.
$ export RUST_LOG=warn
$ ./mach run -d test.html                   # Uses the exported RUST_LOG.
```

See [the `env_logger` docs](https://docs.rs/env_logger/0.11.3/env_logger/index.html#enabling-logging) for more details, but here are some examples:

- to enable all messages up to and including `debug` level, but not `trace`:
  <br>`RUST_LOG=debug`
- to enable all messages from `servo::*`, `servoshell::*`, or any target starting with `servo`:
  <br>`RUST_LOG=servo=trace` (or just `RUST_LOG=servo`)
- to enable all messages from any target starting with `style`, but only `error` and `warn` messages from `style::rule_tree`:
  <br>`RUST_LOG=style,style::rule_tree=warn`

Note that even when a log message is filtered out, it can still impact runtime performance, albeit only slightly.
[Some builds](building-servo.md#build-profiles) of Servo, **including official nightly releases**, remove DEBUG and TRACE messages at compile time, so enabling them with `RUST_LOG` will have no effect.

### Event tracing

In the **constellation**, the **compositor**, and **servoshell**, we log messages sent to and received from other components, using targets of the form `component>other@Event` or `component<other@Event`.
This means you can select which event types to log at runtime with `RUST_LOG`!

For example, in the **constellation** ([more details](https://github.com/servo/servo/blob/bccbc87db7b986cae31c8f14f0a130336f8417b2/components/constellation/tracing.rs)):

- to trace only events from script:
  <br>`RUST_LOG='constellation-from-=off,constellation-from-script:'`
- to trace all events except for ReadyToPresent events:
  <br>`RUST_LOG='constellation-from-,constellation-from-compositor:ReadyToPresent=off'`
- to trace only script InitiateNavigateRequest events:
  <br>`RUST_LOG='constellation-from-=off,constellation-from-script:InitiateNavigateRequest'`

In the **compositor** ([more details](https://github.com/servo/servo/blob/bccbc87db7b986cae31c8f14f0a130336f8417b2/components/compositing/tracing.rs)):

- to trace only MoveResizeWebView events:
  <br>`RUST_LOG='compositor-from-constellation:MoveResizeWebView'`
- to trace all events except for Forwarded events:
  <br>`RUST_LOG=compositor-from-,compositor-from-constellation:Forwarded=off`

In **servoshell** ([more details](https://github.com/servo/servo/blob/bccbc87db7b986cae31c8f14f0a130336f8417b2/ports/servoshell/tracing.rs)):

- to trace only events from servo:
  <br>`RUST_LOG='servoshell-from-=off,servoshell-to-=off,servoshell-from-servo:'`
- to trace all events except for AxisMotion events:
  <br>`RUST_LOG='servoshell-from-,servoshell-to-,servoshell-from-winit:WindowEvent:AxisMotion=off'`
- to trace only winit window moved events:
  <br>`RUST_LOG='servoshell-from-=off,servoshell-to-=off,servoshell-from-winit:WindowEvent:Moved'`

Event tracing can generate an unwieldy amount of output.
In general, we recommend the following config to keep things usable:

- `constellation-from-,constellation-to-,constellation-from-compositor:ForwardEvent:MouseMoveEvent=off,constellation-from-compositor:LogEntry=off,constellation-from-compositor:ReadyToPresent=off,constellation-from-script:LogEntry=off`
- `compositor-from-,compositor-to-`
- `servoshell-from-,servoshell-to-,servoshell-from-winit:DeviceEvent=off,servoshell-from-winit:MainEventsCleared=off,servoshell-from-winit:NewEvents:WaitCancelled=off,servoshell-from-winit:RedrawEventsCleared=off,servoshell-from-winit:RedrawRequested=off,servoshell-from-winit:UserEvent:WakerEvent=off,servoshell-from-winit:WindowEvent:CursorMoved=off,servoshell-from-winit:WindowEvent:AxisMotion=off,servoshell-from-servo:EventDelivered=off,servoshell-from-servo:ReadyToPresent=off,servoshell-to-servo:Idle=off,servoshell-to-servo:MouseWindowMoveEventClass=off`

## Other debug logging

`mach run` does this automatically, but to print a backtrace when Servo panics:

```sh
$ RUST_BACKTRACE=1 target/debug/servo test.html
```

Use `-Z` (`-- --debug`) to enable debug options.
For example, to print the stacking context tree after each layout, or get help about these options:

```sh
$ ./mach run -Z dump-stacking-context-tree test.html
$ ./mach run -Z help            # Lists available debug options.
$ ./mach run -- --debug help    # Same as above: lists available debug options.
$ ./mach run --debug            # Not the same! This just chooses target/debug.
```

On macOS, you can also add some Cocoa-specific debug options, after an extra `--`:

```sh
$ ./mach run -- test.html -- -NSShowAllViews YES
```

## Running servoshell with a debugger

To run servoshell with a debugger, use `--debugger-cmd`.
Note that if you choose `gdb` or `lldb`, we automatically use `rust-gdb` and `rust-lldb`.

```sh
$ ./mach run --debugger-cmd=gdb test.html   # Same as `--debugger-cmd=rust-gdb`.
$ ./mach run --debugger-cmd=lldb test.html  # Same as `--debugger-cmd=rust-lldb`.
```

To pass extra options to the debugger, you’ll need to run the debugger yourself:

```sh
$ ./mach run --debugger-cmd=gdb -ex=r test.html         # Passes `-ex=r` to servoshell.
$ rust-gdb -ex=r --args target/debug/servo test.html    # Passes `-ex=r` to gdb.

$ ./mach run --debugger-cmd=lldb -o r test.html         # Passes `-o r` to servoshell.
$ rust-lldb -o r -- target/debug/servo test.html        # Passes `-o r` to lldb.

$ ./mach run --debugger-cmd=rr -M test.html             # Passes `-M` to servoshell.
$ rr record -M target/debug/servo test.html             # Passes `-M` to rr.
```

Many debuggers need extra options to separate servoshell’s arguments from their own options, and `--debugger-cmd` will pass those options automatically [for a few debuggers](https://github.com/servo/servo/blob/bccbc87db7b986cae31c8f14f0a130336f8417b2/third_party/mozdebug/mozdebug/mozdebug.py#L32-L48), including `gdb` and `lldb`.
For other debuggers, `--debugger-cmd` will only work if the debugger needs no extra options:

```sh
$ ./mach run --debugger-cmd=rr test.html                    # Good, because it’s...
#  servoshell arguments        ^^^^^^^^^
$ rr target/debug/servo test.html                           # equivalent to this.
#  servoshell arguments ^^^^^^^^^

$ ./mach run --debugger-cmd=renderdoccmd capture test.html  # Bad, because it’s...
#                renderdoccmd arguments? ^^^^^^^
#                  servoshell arguments          ^^^^^^^^^
$ renderdoccmd target/debug/servo capture test.html         # equivalent to this.
# => target/debug/servo is not a valid command.

$ renderdoccmd capture target/debug/servo test.html         # Good.
#              ^^^^^^^ renderdoccmd arguments
#                    servoshell arguments ^^^^^^^^^
```

## Debugging with gdb or lldb

To search for a function by name or regex:

```
(lldb) image lookup -r -n <name>
(gdb) info functions <name>
```

To list the running threads:

```
(lldb) thread list
(lldb) info threads
```

Other commands for gdb or lldb include:

```
(gdb) b a_servo_function    # Add a breakpoint.
(gdb) run                   # Run until breakpoint is reached.
(gdb) bt                    # Print backtrace.
(gdb) frame n               # Choose the stack frame by its number in `bt`.
(gdb) next                  # Run one line of code, stepping over function calls.
(gdb) step                  # Run one line of code, stepping into function calls.
(gdb) print varname         # Print a variable in the current scope.
```

See [this gdb tutorial](http://www.unknownroad.com/rtfm/gdbtut/gdbtoc.html) or [this lldb tutorial](https://lldb.llvm.org/tutorial.html) more details.

To inspect variables in lldb, you can also type `gui`, then use the arrow keys to expand variables:

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

If lldb crashes on certain lines involving the `profile()` function, it’s not just you.
Comment out the profiling code, and only keep the inner function, and that should do it.

## Reversible debugging with rr (Linux only)

[rr](https://rr-project.org) is like gdb, but lets you rewind.
Start by running servoshell via rr:

```sh
$ ./mach run --debugger=rr test.html    # Either this...
$ rr target/debug/servo test.html       # ...or this.
```

Then replay the trace, using gdb commands or rr commands:

```
$ rr replay
(rr) continue
(rr) reverse-cont
```

To run one or more tests repeatedly until the result is unexpected:

```sh
$ ./mach test-wpt --chaos path/to/test [path/to/test ...]
```

Traces recorded by rr can take up a lot of space.
To delete them, go to `~/.local/share/rr`.

## OpenGL debugging with RenderDoc (Linux or Windows only)

[RenderDoc](https://renderdoc.org/docs/) lets you debug Servo’s OpenGL activity.
Start by running servoshell via renderdoccmd:

```sh
$ renderdoccmd capture -d . target/debug/servo test.html
```

While servoshell is running, run `qrenderdoc`, then choose **File** > **Attach to Running Instance**.
Once attached, you can press **F12** or **Print Screen** to capture a frame.
