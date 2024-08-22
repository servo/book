# Running servoshell

Assuming you’re in the directory containing `servo`, you can run servoshell with:

```sh
$ ./servo [url] [options]
```

Use `--help` to list the available command line options:

```sh
$ ./servo --help
```

Use `--pref` to [configure Servo’s behaviour](https://github.com/servo/servo/blob/main/resources/prefs.json), including to enable experimental web platform features.
For example, to run our [Conway’s Game of Life demo](https://demo.servo.org/experiments/webgpu-game-of-life/) with WebGPU enabled:

```sh
$ ./servo --pref dom.webgpu.enabled https://demo.servo.org/experiments/webgpu-game-of-life/
```

Use `--devtools=6080` to enable support for [debugging pages with Firefox devtools](hacking/using-devtools.md):

```sh
$ ./servo --devtools=6080
```

## Built servoshell yourself?

When you build it yourself, servoshell will be in `target/debug/servo` or `target/release/servo`.
You can run it directly as shown above, but we recommend using [mach](hacking/mach.md) instead.

To run servoshell with mach, replace `./servo` with `./mach run -d --` or `./mach run -r --`, depending on the [build profile](hacking/building-servo.md) you want to run.
For example, both of the commands below run the debug build of servoshell with the same options:

```sh
$ target/debug/servo https://demo.servo.org
$ ./mach run -d -- https://demo.servo.org
```

## Runtime dependencies

On **Linux**, servoshell requires:

* `GStreamer` ≥ 1.18
* `gst-plugins-base` ≥ 1.18
* `gst-plugins-good` ≥ 1.18
* `gst-plugins-bad` ≥ 1.18
* `gst-plugins-ugly` ≥ 1.18
* `libXcursor`
* `libXrandr`
* `libXi`
* `libxkbcommon`
* `vulkan-loader`

## Keyboard shortcuts

- **Ctrl**+`Q` (⌘Q on macOS) exits servoshell
- **Ctrl**+`L` (⌘L on macOS) focuses the location bar
- **Ctrl**+`R` (⌘R on macOS) reloads the page
- **Alt**+`←` (⌘← on macOS) goes back in history
- **Alt**+`→` (⌘→ on macOS) goes forward in history
- **Ctrl**+`=` (⌘= on macOS) increases the page zoom
- **Ctrl**+`-` (⌘- on macOS) decreases the page zoom
- **Ctrl**+`0` (⌘0 on macOS) resets the page zoom
- **Esc** exits fullscreen mode
