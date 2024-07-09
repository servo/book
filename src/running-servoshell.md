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

Use `--devtools=6080` to enable support for [debugging pages with Firefox devtools](https://firefox-source-docs.mozilla.org/devtools-user/about_colon_debugging/index.html#connecting-over-the-network):

```sh
$ ./servo --devtools=6080
```

<div class="warning">

**Note:** devtools support is currently a work in progress ([#32404](https://github.com/servo/servo/issues/32404)).
</div>

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
