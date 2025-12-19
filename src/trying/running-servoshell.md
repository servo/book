# Running servoshell

Assuming you’re in the directory containing `servo`, you can run servoshell with:

```sh
$ ./servo [url] [options]
```

Use `--help` to list the available command line options:

```sh
$ ./servo --help
```

### Enabling experimental web platform features

Servo has in-progress support for many web platform features.
Some are not complete enough to be enabled by default, but you can try them out using a preference setting.
For a list of these features and the preference used to enable them, see [Experimental Web Platform Features](../design-documentation/experimental-features.md].
In addition, you can enable a useful subset of these features with the `--enable-experimental-web-platform-features` command-line argument or via the servoshell user interface.

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

## Troubleshooting

servoshell should run on most systems without any need to install dependencies.
If you are on **Linux** and servoshell reports that a shared library is missing, ensure that you have the following packages installed:

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
