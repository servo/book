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

**Note:** devtools support is currently broken ([#29831](https://github.com/servo/servo/issues/29831)).
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
