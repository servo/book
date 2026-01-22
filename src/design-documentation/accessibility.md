# Accessibility

## Central cache

Servo retains a central cache of the whole accessibility tree in the main process ([embedder process](architecture.md)).
This is the same basic principle as the accessibility architecture of Chromium ([docs](https://chromium.googlesource.com/chromium/src/+/d779ec8c0ed366ee689e3a30132b9b8c98a9a941/docs/accessibility/browser/how_a11y_works_2.md)), Firefox ([Cache the World](https://www.jantrid.net/2022/12/22/Cache-the-World/)), and [AccessKit](https://accesskit.dev) ([how it works](https://accesskit.dev/how-it-works/)).
Since assistive technologies need to query the tree frequently and synchronously, caching the tree centrally allows them to do so without incurring IPC latency or interrupting web content processes.

We do this by sending AccessKit [tree updates](https://docs.rs/accesskit/0.23.0/accesskit/struct.TreeUpdate.html) from layout (in web content processes) to an embedder-provided AccessKit adapter (in the main process), such as [accesskit_winit](https://docs.rs/accesskit_winit/0.31.1/accesskit_winit/struct.Adapter.html).
Internally the adapter uses [accesskit_consumer](https://docs.rs/accesskit_consumer/0.33.1/accesskit_consumer/) to retain the tree.
