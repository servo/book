# Accessibility

This section contains information on the design of Servo's accessibility system.

**[Background](background.md)** provides information on the goals of the accessibility system, and on [AccessKit](https://accesskit.dev/), the library we use to provide cross-platform accessibility support.

**[Servo accessibility for embedders](for-embedders.md)** explains the embedder APIs for activating accessibility and consuming accessibility information produced by Servo.

**[(TODO) servoshell accessibility](servoshell.md)** will describe how we use the embedder API to embed Servo's accessibility trees in the servoshell application.

**[WebView accessibility internals](webview-internals.md)** explains how accessibility activation for a particular webview is implemented.

**[Generating accessibility trees for web content](tree.md)** explains how the tree for a particular web page is created and updated.

**[(TODO) Servo accessibility tree testing](testing.md)** will describe how we test the correctness of our accessibility tree implementation.

## `accessibility_enabled` pref

While the system is being developed, the [`accessibility_enabled`](https://doc.servo.org/servo/prefs/struct.Preferences.html#structfield.accessibility_enabled) pref must be set in order to enable the accessibility code to run.

> [!NOTE]
> As well as enabling the pref, it may be necessary to have an assistive technology running in order for the accessibility tree to be built and exposed to accessibility inspectors. On Linux, running [Orca](https://orca.gnome.org/) is sufficient. [Accerciser](https://gitlab.gnome.org/GNOME/accerciser) or [Elevado](https://gitlab.gnome.org/feaneron/elevado/) can be used to inspect the accessibility tree as it is exposed to assistive technologies.

