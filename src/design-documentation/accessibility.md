# Accessibility

## Central cache

Applications using Servo must retain a central cache of the whole accessibility tree in the main process ([embedder process](architecture.md)).
This is the same basic principle as the accessibility architecture of Chromium ([docs](https://chromium.googlesource.com/chromium/src/+/d779ec8c0ed366ee689e3a30132b9b8c98a9a941/docs/accessibility/browser/how_a11y_works_2.md)), Firefox ([Cache the World](https://www.jantrid.net/2022/12/22/Cache-the-World/)), and [AccessKit](https://accesskit.dev) ([how it works](https://accesskit.dev/how-it-works/)).
Since assistive technologies need to query the tree frequently and synchronously, caching the tree centrally allows them to do so without incurring IPC latency or interrupting web content processes.

We do this by sending AccessKit [tree updates](https://docs.rs/accesskit/0.23.0/accesskit/struct.TreeUpdate.html) from layout (in web content processes) to an embedder-provided AccessKit adapter (in the main process), such as [accesskit_winit](https://docs.rs/accesskit_winit/0.31.1/accesskit_winit/struct.Adapter.html).
Internally the adapter uses [accesskit_consumer](https://docs.rs/accesskit_consumer/0.33.1/accesskit_consumer/) to retain the tree.

## Subtrees

That whole accessibility tree is made up of subtrees that are built by different parties.
The subtrees for each webview and document within that webview are built by the layout engine for that document, and the subtrees for any surrounding UI elements are built by the embedder.

This creates some problems: we want to allow these different parties to build and update their subtrees independently of one another, on their own schedules, and use whatever [NodeId](https://docs.rs/accesskit/0.23.0/accesskit/struct.NodeId.html) values they like without worrying about conflicts.

Ad-hoc schemes for avoiding NodeId conflicts are problematic here.
The type is only 64 bits wide, which is wide enough to avoid needing to [handle overflow](https://source.chromium.org/chromium/chromium/src/+/main:third_party/blink/renderer/modules/accessibility/ax_object_cache_impl.cc;l=2187-2215;drc=068b7e346d819075983f831a853bdf1da287973c), but not wide enough to [reliably avoid collisions between random values](https://en.wikipedia.org/wiki/Birthday_attack).
If we partition the bits of NodeId into a “subtree id” and “local node id”, even in the most balanced case with 32 bits for each, both parts now need to worry about handling overflow.

In our initial proposal ([accesskit#641](https://github.com/AccessKit/accesskit/pull/641)), we considered adding support for subtrees at the adapter level, introducing a “wrapper” or “meta” adapter that statefully remaps every NodeId to another globally unique NodeId, using hash maps to guarantee uniqueness.
This was cumbersome and unlikely to be performant.

The subtree feature that shipped ([accesskit#655](https://github.com/AccessKit/accesskit/pull/655)) solves these problems at the schema level by allowing tree updates to [specify](https://docs.rs/accesskit/0.23.0/accesskit/struct.TreeUpdate.html#structfield.tree_id) a 128-bit [TreeId](https://docs.rs/accesskit/0.23.0/accesskit/struct.TreeId.html), such that each node is uniquely identified by the tuple ([TreeId](https://docs.rs/accesskit/0.23.0/accesskit/struct.TreeId.html), [NodeId](https://docs.rs/accesskit/0.23.0/accesskit/struct.NodeId.html)).
To configure how the subtrees are combined, a [Node](https://docs.rs/accesskit/0.23.0/accesskit/struct.Node.html) can be [designated](https://docs.rs/accesskit/0.23.0/accesskit/struct.Node.html#method.tree_id) as a graft node for some other subtree.

> [!NOTE]
> The adapter [internally maps this](https://docs.rs/accesskit_consumer/0.33.1/src/accesskit_consumer/node.rs.html#29-51) to another tuple (32-bit tree index, NodeId), forming a 96-bit value that gets exposed to the platform, but uniqueness of tree indices is managed by the adapter, so this is mostly an implementation detail that limits us to <math><msup><mn>2</mn><mn>32</mn></msup></math> concurrent subtrees.
