<!-- TODO: needs copyediting -->

# Profiling

When profiling Servo or troubleshooting performance issues, make sure your build is optimised while still allowing for accurate profiling data.

```sh
./mach build --profile profiling --with-frame-pointer
```

- **--profile profiling** builds Servo with [our profiling configuration](../building/building.md#build-profiles)
- **--with-frame-pointer** builds Servo with stack frame pointers on all platforms

The matching profile needs to be selected when running Servo:

```sh
./mach run --profile profiling http://example.org
```

Several ways to get profiling information about Servo's runs:
* [Tracing with Perfetto](#tracing-with-perfetto)
* [Interval Profiling](#interval-profiling)
  * [TSV Profiling](#tsv-profiling)
  * [Generating Timelines](#generating-timelines)
  * [Built-in sampling profiler](#sampling-profiler)
* [Memory Profiling](#memory-profiling)
* [Using macOS Instruments](#using-macos-instruments)


## Tracing with Perfetto

Tracing works by instrumenting specific functions (or portions of code) with explicit annotations such as `time_profile!` and `servo_tracing::*`.
It deterministically records every call through instrumented code, but does not provide any visibility into code that is not instrumented.

In contrast, sampling profilers can see everything but only probabilistically and thus get more accurate with long-running loops.

To use tracing, enable related compile-time features:

```sh
./mach build --profile profiling --features tracing tracing-perfetto
```

Then run Servo with the `SERVO_TRACING` environment variable set to [`EnvFilter` directives] to select which traces to enable:

```
SERVO_TRACING=… ./mach run --profile profiling http://example.org
```

For example:

- `SERVO_TRACING=off` disables all tracing (this is the default)
- `SERVO_TRACING=trace` enables all tracing (yields massive traces due to `compositing`)
- `SERVO_TRACING=[{servo_profiling}]` does the same, since we implicitly filter on `servo_profiling`
- `SERVO_TRACING=info` would enable only the `info` level and above, but we don’t yet use levels
- `SERVO_TRACING=layout` enables tracing in the `layout` crate only
- `SERVO_TRACING=trace,compositing=off` enables all tracing except in the `compositing` crate
- `SERVO_TRACING=[handle_reflow]` enables tracing in spans named “handle_reflow” *or their descendants*

This creates a `servo.pftrace` file in the current directory, which can be visualized in [ui.perfetto.dev](https://ui.perfetto.dev/).

[`EnvFilter` directives]: https://docs.rs/tracing-subscriber/0.3.23/tracing_subscriber/filter/struct.EnvFilter.html#directives


## Interval Profiling

Using the -p option followed by a number (time period in seconds), you can spit out profiling information to the terminal periodically.
To do so, run Servo on the desired site (URLs and local file paths are both supported) with profiling enabled:

```
./mach run --profile profiling http://example.org -p 5
```

In the example above, while Servo is still running (AND is processing new passes), the profiling information is printed to the terminal every 5 seconds.

Once the page has loaded, hit ESC (or close the app) to exit.
Profiling output will be provided, broken down by area of the browser and URL.
For example, you might get output of the form below:

```
_category_                          _incremental?_ _iframe?_             _url_                  _mean (ms)_   _median (ms)_      _min (ms)_      _max (ms)_       _events_ 
Painting                                N/A          N/A                  N/A                        6.8177          0.9512          0.0035         30.7573               6
Layout                                  yes          yes     http://example.org/                     0.0016          0.0016          0.0016          0.0016               1
Layout                                  no           yes     http://example.org/                    14.4966         14.4966         14.4966         14.4966               1
ScriptParseHTML                         no           yes     http://example.org/                     0.8507          1.7009          0.0004          1.7009               2
TimeToFirstPaint                        no           yes     http://example.org/                     0.0000          0.0000          0.0000          0.0000               1
TimeToFirstContentfulPaint              no           yes     http://example.org/                     0.0000          0.0000          0.0000          0.0000               1

_url_   _blocked layout queries_

```

In this example, when loading the page we performed one full layout and one incremental layout passes.

### TSV Profiling

Using the -p option followed by a file name, you can spit out profiling information of Servo's execution to a TSV (tab-separated because certain url contained commas) file.
The information is written to the file only upon Servo's termination.
This works well with the `-x`, `-z`, and `-o` options so that performance information can be collected during automated runs.
Example usage:

```
./mach run --profile profiling http://example.org -zxo out.png -p out.tsv
```

The formats of the profiling information in the Interval and TSV Profiling options are the essentially the same; the url names are not truncated in the TSV Profiling option.

### Generating Timelines

Add the `--profiler-trace-path /timeline/output/path.html` flag to output the profiling data as a self contained HTML timeline.
Because it is a self contained file (all CSS and JS is inline), it is easy to share, upload, or link to from bug reports.

```
./mach run --profile profiling http://example.org -p 5 --profiler-trace-path trace.html
```

#### Usage:

* Use the mouse wheel or trackpad scrolling, with the mouse focused along the top of the timeline, to zoom the viewport in or out.

* Grab the selected area along the top and drag left or right to side scroll.

* Hover over a trace to show more information.

#### Hacking

The JS, CSS, and HTML for the timeline comes from [fitzgen/servo-trace-dump](https://github.com/fitzgen/servo-trace-dump/) and there is a script in that repo for updating servo's copy.

All other code is in the `components/profile/` directory.

## Sampling profiler

Servo includes a sampling profiler which generates profiles that can be opened in the [Gecko profiling tools](https://profiler.firefox.com/).
To use them:

1. Run Servo, loading the page you wish to profile
2. Press Ctrl+P (or Cmd+P on macOS) to start the profiler (the console should show "Enabling profiler")
3. Press Ctrl+P (or Cmd+P on macOS) to stop the profiler (the console should show "Stopping profiler")
4. Keep Servo running until the symbol resolution is complete (the console should show a final "Resolving N/N")
5. Run `python etc/profilicate.py samples.json >gecko_samples.json` to transform the profile into a format that the Gecko profiler understands
6. Load `gecko_samples.json` into https://profiler.firefox.com/

To control the output filename, set the `PROFILE_OUTPUT` environment variable.
To control the sampling rate (default 10ms), set the `SAMPLING_RATE` environment variable.

## Memory Profiling

* Run Servoshell normally
* Open a new tab
* Navigate to `about:memory`
* Click `Measure`
* See a report similar to this:

```
  115.15 MiB -- explicit
     101.15 MiB -- jemalloc-heap-unclassified
      14.00 MiB -- url(http://example.org/)
         10.01 MiB -- layout-thread
            10.00 MiB -- font-context
             0.00 MiB -- stylist
             0.00 MiB -- display-list
          4.00 MiB -- js
             2.75 MiB -- malloc-heap
             1.00 MiB -- gc-heap
                0.56 MiB -- decommitted
                0.35 MiB -- used
                0.06 MiB -- unused
                0.02 MiB -- admin
             0.25 MiB -- non-heap
       0.00 MiB -- memory-cache
          0.00 MiB -- private
          0.00 MiB -- public

  121.89 MiB -- jemalloc-heap-active
  111.16 MiB -- jemalloc-heap-allocated
  203.02 MiB -- jemalloc-heap-mapped
  272.61 MiB -- resident
```

## Using macOS Instruments

Xcode has a [instruments](https://help.apple.com/instruments/mac/10.0/) tool to profile easily.

First, you need to install Xcode instruments:

```
xcode-select --install
```

Second, install `cargo-instruments` via Homebrew:

```
brew install cargo-instruments
```

Then, you can simply run it via CLI:

```
cargo instruments -t Allocations
```

Here are some links and resources for help with Instruments (Some will stream only on Safari):
* [cargo-instruments on crates.io](https://crates.io/crates/cargo-instruments)
* [Using Time Profiler in Instruments](https://developer.apple.com/videos/play/wwdc2016/418/)
* [Profiling in Depth](https://developer.apple.com/videos/play/wwdc2015/412/)
* [System Trace in Depth](https://developer.apple.com/videos/play/wwdc2016/411/)
  * Threads, virtual memory, and locking
* [Core Data Performance Optimization and Debugging](https://developer.apple.com/videos/play/wwdc2013/211/)
* [Learning Instruments](https://developer.apple.com/videos/play/wwdc2012/409/)


## Profiling WebRender

When running Servoshell, press CTRL+F12 to show (or hide) the WebRender overlay.


## Webpage snapshots

It is possible to use the `mitmproxy` tool to intercept servo traffic and create local snapshot (dump) of an arbitrary web-page, to then serve locally for profiling purposes.

`mitmproxy` support several ways to intersept the traffic including a `proxy` mode at port `:8080`, so you can set the browser to just:

```bash
./target/release/servo \
--pref=network_http_proxy_uri=http://127.0.0.1:8080 \
--ignore-certificate-errors 
```

> [!info] The default `mitmproxy` certs are in the `~/.mitmproxy` or you can generate some using `mitmproxy`, but I have just set my browser to ignore cert errors

> [!warning] ignoring certs is easy, but be cautious of risks

### Default mitmproxy

On a default network, the mitmproxy creates a local proxy server at `:8080` and by setting it in browser or passing `http_proxy=locahost:8080` and/or `https_proxy=localhost:8080` (and by optionally unsetting the `no_proxy`) you can dump and serve the traffic.

#### Creating a dump
```bash
mitmproxy -w <dumpfile>
```

#### Serving a dump
```bash
mitmproxy --serve-replay <dumpfile>
```

The resulted dump file is about `~5MB` per page, so it can get large pretty fast, as the tool is very verbose and can store pictures.

### Chain-proxy
In case of a another primary proxy connection, we need to pass the `upstream` to the main proxy from `mitmproxy` and if the main proxy also has custom certificates, it is crucial to pass them, or to ignore them
> [!warning] ignoring certs is easy, but be cautious of risks
#### Creating a dump
```bash
mitmproxy  --mode upstream:${http_proxy} -w <dump-path>\
--set ssl_insecure=true
#### Serving the dump
```bash
mitmproxy -v  --server-replay ~/dev/recodings/servo_org_3.dump \
--set server_replay_extra=404 \
--set server_replay_ignore_host=true \
--set connection_strategy=lazy \
--set server_replay_reuse=true
```
> [!info] the `replay_extra` and `replay_reuse` are optional, and may cause unexpected behaviour
### OpenHarmony
It is possible to use the tool to intersept remote phone traffic including OpenHarmony targets. Open a reverse proxy port using `hdc` and then run the `servo` with proxy and certs set up.
#### reverse port
```bash
hdc rport tcp:8080 tcp:8080
```
#### run with args
```bash
hdc shell aa start -a EntryAbility \
-b org.servo.servo -U https://servo.org \
--psn=--pref=network_http_proxy_uri=http://127.0.0.1:8080 \
--psn=--ignore-certificate-errors
```


