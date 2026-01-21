# Accessibility

Servo retains a central cache of the whole accessibility tree in the main process ([embedder process](architecture.md)).
This is the same basic principle as the accessibility architecture of Chromium ([docs](https://chromium.googlesource.com/chromium/src/+/d779ec8c0ed366ee689e3a30132b9b8c98a9a941/docs/accessibility/browser/how_a11y_works_2.md)), Firefox ([Cache the World](https://www.jantrid.net/2022/12/22/Cache-the-World/)), and even [AccessKit](https://accesskit.dev) ([how it works](https://accesskit.dev/how-it-works/)), which our accessibility support is based on.
Since assistive technologies need to query the tree synchronously, caching the tree centrally allows them to do so without incurring IPC latency or interrupting web content processes.
