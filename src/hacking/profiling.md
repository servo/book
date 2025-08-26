<!-- TODO: needs copyediting -->

# Profiling

When profiling Servo or troubleshooting performance issues, make sure your build is optimised while still allowing for accurate profiling data.

```sh
$ ./mach build --profile profiling --with-frame-pointer
```

- **--profile profiling** builds Servo with [our profiling configuration](building-servo.md#build-profiles)
- **--with-frame-pointer** builds Servo with stack frame pointers on all platforms

Several ways to get profiling information about Servo's runs:
* [Interval Profiling](#interval-profiling)
  * [TSV Profiling](#tsv-profiling)
  * [Generating Timelines](#generating-timelines)
  * [Built-in sampling profiler](#sampling-profiler)
* [Memory Profiling](#memory-profiling)
* [Using macOS Instruments](#using-macos-instruments)

## Interval Profiling

Using the -p option followed by a number (time period in seconds), you can spit out profiling information to the terminal periodically.
To do so, run Servo on the desired site (URLs and local file paths are both supported) with profiling enabled:
```
 ./mach run --release -p 5 https://www.cnn.com/
```

In the example above, while Servo is still running (AND is processing new passes), the profiling information is printed to the terminal every 5 seconds.

Once the page has loaded, hit ESC (or close the app) to exit.
Profiling output will be provided, broken down by area of the browser and URL.
For example, if you would like to profile loading Hacker News, you might get output of the form below:
```
[larsberg@lbergstrom servo]$ ./mach run --release -p 5 http://news.ycombinator.com/
_category_                          _incremental?_ _iframe?_             _url_                  _mean (ms)_   _median (ms)_      _min (ms)_      _max (ms)_       _events_ 
Compositing                             N/A          N/A                  N/A                        0.0440          0.0440          0.0440          0.0440               1
Layout                                  no           no      https://news.ycombinator.com/          29.8497         29.8497         29.8497         29.8497               1
Layout                                  yes          no      https://news.ycombinator.com/          11.0412         10.9748         10.8149         11.3338               3
+ Style Recalc                          no           no      https://news.ycombinator.com/          22.8149         22.8149         22.8149         22.8149               1
+ Style Recalc                          yes          no      https://news.ycombinator.com/           5.3933          5.2915          5.2727          5.6157               3
+ Restyle Damage Propagation            no           no      https://news.ycombinator.com/           0.0135          0.0135          0.0135          0.0135               1
+ Restyle Damage Propagation            yes          no      https://news.ycombinator.com/           0.0146          0.0149          0.0115          0.0175               3
+ Primary Layout Pass                   no           no      https://news.ycombinator.com/           3.3569          3.3569          3.3569          3.3569               1
+ Primary Layout Pass                   yes          no      https://news.ycombinator.com/           2.8727          2.8472          2.8279          2.9428               3
| + Parallel Warmup                     no           no      https://news.ycombinator.com/           0.0002          0.0002          0.0002          0.0002               2
| + Parallel Warmup                     yes          no      https://news.ycombinator.com/           0.0002          0.0002          0.0001          0.0002               6
+ Display List Construction             no           no      https://news.ycombinator.com/           3.4058          3.4058          3.4058          3.4058               1
+ Display List Construction             yes          no      https://news.ycombinator.com/           2.6722          2.6523          2.6374          2.7268               3
```

In this example, when loading the page we performed one full layout and three incremental layout passes, for a total of (29.8497 + 11.0412 * 3) = 62.9733ms.

### TSV Profiling

Using the -p option followed by a file name, you can spit out profiling information of Servo's execution to a TSV (tab-separated because certain url contained commas) file.
The information is written to the file only upon Servo's termination.
This works well with the -x OR -o option so that performance information can be collected during automated runs.
Example usage:
```
./mach run -r -o out.png -p out.tsv https://www.google.com/
```
The formats of the profiling information in the Interval and TSV Profiling options are the essentially the same; the url names are not truncated in the TSV Profiling option.

### Generating Timelines

Add the `--profiler-trace-path /timeline/output/path.html` flag to output the profiling data as a self contained HTML timeline.
Because it is a self contained file (all CSS and JS is inline), it is easy to share, upload, or link to from bug reports.

    $ ./mach run --release -p 5 --profiler-trace-path trace.html https://reddit.com/

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

Using the -m option followed by a number (time period in seconds), you can spit out profiling information to the terminal periodically.
To do so, run Servo on the desired site (URLs and local file paths are both supported) with profiling enabled:
```
./mach run --release -m 5 http://example.com/
```

In the example above, while Servo is still running (AND is processing new passes), the profiling information is printed to the terminal every 5 seconds.

```
./mach run --release -m 5 http://example.com/
Begin memory reports 5
|
|  115.15 MiB -- explicit
|     101.15 MiB -- jemalloc-heap-unclassified
|      14.00 MiB -- url(http://example.com/)
|         10.01 MiB -- layout-thread
|            10.00 MiB -- font-context
|             0.00 MiB -- stylist
|             0.00 MiB -- display-list
|          4.00 MiB -- js
|             2.75 MiB -- malloc-heap
|             1.00 MiB -- gc-heap
|                0.56 MiB -- decommitted
|                0.35 MiB -- used
|                0.06 MiB -- unused
|                0.02 MiB -- admin
|             0.25 MiB -- non-heap
|       0.00 MiB -- memory-cache
|          0.00 MiB -- private
|          0.00 MiB -- public
|
|  121.89 MiB -- jemalloc-heap-active
|  111.16 MiB -- jemalloc-heap-allocated
|  203.02 MiB -- jemalloc-heap-mapped
|  272.61 MiB -- resident
|404688.75 MiB -- vsize
|
End memory reports
```

## Using macOS Instruments

Xcode has a [instruments](https://help.apple.com/instruments/mac/10.0/) tool to profile easily.

First, you need to install Xcode instruments:

```
$ xcode-select --install
```

Second, install `cargo-instruments` via Homebrew:

```
$ brew install cargo-instruments
```

Then, you can simply run it via CLI:

```
$cargo instruments -t Allocations
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

Use the following command to get some profile data from WebRender:

    $ ./mach run -w -Z wr-stats --release http://www.nytimes.com

When you run Servo with this command, you'll be looking at three things:

- CPU (backend):    The amount of time WebRender is packing and batching data.
- CPU (Compositor): Amount of time WebRender is issuing GL calls and interacting with the driver.
- GPU: Amount of time the GPU is taking to execute the shaders.
