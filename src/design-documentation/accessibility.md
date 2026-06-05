# Accessibility

## TODO: patch analysis

- [layout: Split recompute_children() from update_node() in AccessibilityTree.](https://github.com/servo/servo/pull/44768)
    - towards a future where we traverse the accessibility tree instead of the DOM tree (for aria-owns?)
    - ended up refactoring the methods, which could help with profiling
- [#44767](https://github.com/servo/servo/pull/44767)
    - accessibility node ids are sequential u64
    - u64 is big enough that Servo can create 2^32 new nodes per second for 136 years without overflow, so we don’t need to do anything special to avoid collisions.
    - accessibility node ids can outlive DOM nodes in the AT and in action requests, so decoupling the ids from DOM node addresses is necessary to avoid potential incorrect targeting of action requests when a DOM node has since been freed and its address reused
- [#44766](https://github.com/servo/servo/pull/44766)
    - setters/getters are purely procedural
    - node mutations now set updated flag on AccessibilityNode (which controls whether the node goes in the TreeUpdate), rather than ad-hoc bubbling out to locals, which made it easy to only set updated when a property genuinely has a different value
- [#44473](https://github.com/servo/servo/pull/44473)
    - fix crash when reloading; we deactivate a11y when navigating away from a page, which includes reloading, but when reloading, the pipeline seems to get closed before we can deactivate accessibility. so ignore attempts to deactivate a11y on closed pipelines (because that’s a normal part of reloading), but log an error without panicking when activating a11y on closed pipelines (which should in theory never happen)
- [#44439](https://github.com/servo/servo/pull/44439)
    - implement name from content <https://w3c.github.io/aria/#namefromcontent>, walking the accessibility tree
- [#44438](https://github.com/servo/servo/pull/44438)
    - use ArcRefCell, like the rest of layout, because classical ownership means that all of your methods have to be (&mut self), which means the whole tree is tied up, and together that means you can’t make (&self) helper methods that read from the tree. also this causes problems for recursion?
- [#44437](https://github.com/servo/servo/pull/44437)
    - dedupe nodes that get changed multiple times within one TreeUpdate (don’t remember if this happens in practice?)
- [#44255](https://github.com/servo/servo/pull/44255)
    - build a minimal tree with some non-interactive roles like paragraphs and headings, rather than just text nodes and generic containers
- [#44208](https://github.com/servo/servo/pull/44208)
    - don’t send a message for the tree update from layout to script, because layout now runs on the script thread, just send it to libservo directly
- [#43772](https://github.com/servo/servo/pull/43772)
    - don’t send an empty TreeUpdate for the WebView with no pipeline graft, because it’s not necessary
    - don’t set label on graft nodes, because nothing can see it really (other than consumer API itself)
    - rename method for clarity and make it pub(crate) not pub
- [#43558](https://github.com/servo/servo/pull/43558)
    - in servoshell, activate accessibility in all webviews *and* plumb the webview a11y trees into the app’s main tree, because if we do the former without the latter, accesskit will panic!
- [#43556](https://github.com/servo/servo/pull/43556)
    - graft active top-level pipeline trees into webview trees whenever the webview navigates (including both normal and bfcache navigations)
    - we steer clear of doing anything about iframes, but we expect that the grafts for those will be done by the containing document’s layout (see “Graft node ordering problems in Servo Accessibility” § iframe support)
    - implicit: we detach the a11y tree of the old document when navigating (rather than say, keeping it but somehow marking it “hidden”), which effectively destroys it in accesskit (central cache) and hence the platform. we also deactivate accessibility in the document, which effectively destroys it in our internal tree. combined that means if we do a bfcache navigation, we need to rebuild the a11y tree from scratch, which is unfortunate because it partially defeats the bfcache. maybe we can revisit one or both of these? note that firefox does not retain those trees in the platform at least (not sure about the central cache or internally)
- [#43029](https://github.com/servo/servo/pull/43029)
    - change API from Servo::set_accessibility_active to WebView::set_accessibility_active
    - aligns more closely with the fact that embedders get an accesskit subtree per webview, and need to graft the subtrees for each webview into the app’s main tree
    - new API design encourages correct use by returning the TreeId with each WebView::set_accessibility_active call
    - internally move from activating all documents in each ScriptThread, to activating one document at a time
        - may have proved useful later for bfcache navigation, where we have to deactivate a11y upon navigating away
- [#43013](https://github.com/servo/servo/pull/43013)
    - add active_top_level_pipeline_id field and update it when the frame tree changes
    - later became Option, because we found that our logic relied on the None → Some transition for new tabs/windows
- [#43012](https://github.com/servo/servo/pull/43012)
    - introduces the three levels of grafts (embedder to webview, webview to pipeline, and pipeline to pipeline)
    - if pipelines generate random TreeId, they need to communicate it to the constellation somehow
        - this is asynchronous, so more plumbing and more potential for timing problems
    - instead we derive a TreeId from the PipelineId as a UUIDv5, which the constellation can do on its own
    - caveat: now you can’t run more than one `Servo` in an application (if that was even possible before?)
- [#42402](https://github.com/servo/servo/pull/42402)
    - update accesskit to include subtree support; we had to coordinate updates in egui and kittest also
- [#42338](https://github.com/servo/servo/pull/42338)
    - initial tree building in layout
    - observes that if the constellation sends a TreeId to libservo, and script sends a TreeUpdate to libservo, there’s no guarantee that the TreeId is received before the TreeUpdate, even though it was the constellation that originally kicked off both
    - ordering issues solved with epoch (see “Graft node ordering problems in Servo Accessibility”)
    - to ensure that bfcache navigations work, we also deactivate a11y in the old pipeline when navigating away
- [#42336](https://github.com/servo/servo/pull/42336)
    - old Servo::set_accessibility_active API
    - would activate a11y in all event loops (all script threads), which would in turn activate a11y in all of their documents
- [#42333](https://github.com/servo/servo/pull/42333)
    - pref. note that enabled ≠ active
- [Plumb accessibility tree updates from layout to embedder](https://github.com/servo/servo/pull/41924)
    - plumbing – everything between layout and the embedder
    - has one unnecessary message from layout to script, later eliminated in [#44208](https://github.com/servo/servo/pull/44208)
    - otherwise quite direct, going directly from script thread to embedder’s main thread, no constellation or anything

## Background: AccessKit concepts

[AccessKit](https://accesskit.dev) provides a platform-independent schema for exposing information about the application's UI to assistive technology APIs.

### Accessibility tree

Accessibility information is provided to platform accessibility APIs as a tree of nodes, representing the different parts of the UI - for example, a node representing a toolbar may contain nodes representing buttons.

Platform APIs allow assistive technologies like screen readers to present an alternative user interface (for example, a speech- or braille-based interface) to users, and allow those interfaces to be interacted with via the assistive technology by allowing the assistive technology to relay user interactions back to the application.

A browser's accessibility tree combines the accessibility tree for its own UI (the address bar, and so on) with the accessibility trees for any active documents, so that users can use assistive technology to interact with web pages being shown in the browser.

### Central cache

Since assistive technologies need to query the tree frequently and synchronously, multi-process browsers typically cache the tree centrally to allow them to do so without incurring IPC latency or interrupting web content processes.

This principle is behind the accessibility architecture of Chromium ([docs](https://chromium.googlesource.com/chromium/src/+/d779ec8c0ed366ee689e3a30132b9b8c98a9a941/docs/accessibility/browser/how_a11y_works_2.md)) and Firefox ([Cache the World](https://www.jantrid.net/2022/12/22/Cache-the-World/)).
In these architectures, the main browser process retains an in-memory accessibility tree composed of the tree representing the browser UI plus the sub-trees for any web contents being shown in the browser (including tabs which are currently not showing).
Each renderer process is responsible for communicating _updates_ to its accessibility tree to the main process for incorporation into the aggregated tree.
The accessibility trees are all represented internally in a platform-independent manner, and mapped to the respective platform APIs for the platform the browser is running on.

The [basic design of AccessKit](https://accesskit.dev/how-it-works/) is based on Chromium's original multi-process accessibility architecture, which also influenced Firefox's "Cache the World" design.
It provides a platform-independent, serializable schema centered on the concept of tree updates, as well as an API to allow consuming those updates to create an in-memory tree which can be mapped to platform APIs.
Typically, application developers only need to be concerned with producing the tree updates; AccessKit provides "adapters" which consume the updates, retain the cached full tree, and communicate with platform APIs.

### AccessKit data types

#### `Node`

AccessKit provides a [`Node`](https://docs.rs/accesskit/0.24.0/accesskit/struct.Node.html) type to represent a node in the accessibility tree.
A `Node` _must_ have a [`Role`](https://docs.rs/accesskit/0.24.0/accesskit/enum.Role.html) value, and may have many other properties, including [`children`](https://docs.rs/accesskit/0.24.0/accesskit/struct.Node.html#method.children).

`Node` is designed to be serializable, so it can be easily passed between processes.

#### `NodeId`

Each `Node` is associated with a [`NodeId`](https://docs.rs/accesskit/0.24.0/accesskit/struct.NodeId.html), which must be unique within the node's tree.
Properties which refer to other nodes in the tree, including `children`, refer to nodes by their `NodeId`s.

`Node` doesn't have an ID property; rather, the mechanism for associating a `Node` with a `NodeId` is via `TreeUpdate`.

#### `TreeUpdate`

[`TreeUpdate`](https://docs.rs/accesskit/0.24.0/accesskit/struct.TreeUpdate.html) represents a _change_ to an accessibility tree.
The initial full tree for an application or subtree is sent as a `TreeUpdate` with all known nodes, and the necessary metadata for the tree; subsequent `TreeUpdate`s need only include nodes which have changed and the tree's `TreeId`.
Any node which is added or changed in any way, including adding or removing child nodes, must be included in the `TreeUpdate` in full (i.e. not only changed properties for the node).

Somewhat counter-intuitively, AccessKit doesn't provide a schema for an accessibility tree data structure to be used as a "source" for `TreeUpdate`s - it's up to the application to produce `TreeUpdate`s based on any UI changes in any way it sees fit.

The bulk of each `TreeUpdate` is a vector of `(NodeId, Node)` pairs; each `NodeId` must be unique to the [`TreeId`](https://docs.rs/accesskit/0.24.0/accesskit/struct.TreeId.html) that the `TreeUpdate` refers to.
The rest of the `TreeUpdate` consists of the `TreeId` for the tree, the `NodeId` of the currently focused node, and optionally some metadata about the tree (required if this is the first `TreeUpdate` for this `TreeId`).

Each `TreeUpdate` can only have one `TreeId`; this determines the ID space for the `NodeId`s in the update.

### Subtrees

AccessKit allows applications to nest separate trees to avoid needing to maintain global uniqueness of NodeIds.

Nesting a tree as a subtree of another tree is a two-step process, where the order is critical:

1. Send a `TreeUpdate` for the _parent_ tree which includes a [`Node`](https://docs.rs/accesskit/0.24.0/accesskit/struct.Node.html) with a [`tree_id`](https://docs.rs/accesskit/0.24.0/accesskit/struct.Node.html#method.tree_id) value equal to the `TreeId` of the _child_ tree. This `Node` becomes a _graft node_ for the subtree.
2. Send a `TreeUpdate` for the _child_ tree with the matching [`tree_id`](https://docs.rs/accesskit/0.24.0/accesskit/struct.TreeUpdate.html#structfield.tree_id) value.

Any `TreeUpdate` with a `tree_id` value other than [`TreeId::ROOT`](https://docs.rs/accesskit/0.24.0/accesskit/struct.TreeId.html#associatedconstant.ROOT) MUST be preceded by a `TreeUpdate` containing a `Node` with the same `tree_id` value; otherwise, the AccessKit adapter consuming the `TreeUpdate` will panic.

<img alt="Diagram of subtree grafting: Tree 1 includes a node with tree_id: 2, which is labelled as 'graft node' and has a dotted line pointing to the root node of Tree 2." src="../images/accesskit-graft-node.svg">

### Adapters

`Node`s and `TreeUpdate`s allow an application to describe a platform-independent accessibility tree.
Adapters map between this platform-independent representation and the various platform-specific accessibility APIs.

Typically, an adapter will provide a method which takes a `TreeUpdate`, and uses the [`accesskit_consumer` API](https://docs.rs/accesskit_consumer/latest/accesskit_consumer/index.html) to update an in-memory tree which can be queried via platform APIs, triggering the appropriate notifications to the API in the process.

AccessKit provides platform-specific adapters for Linux, macOS and Windows, as well as a cross-platform [`accesskit_winit`](https://crates.io/crates/accesskit_winit) adapter which can be used by projects using the `winit` cross-platform windowing library.
`accesskit_winit` pulls in the respective platform-specific adapters under the hood.

### Actions

Finally, AccessKit provides an [`ActionRequest`](https://docs.rs/accesskit/0.24.0/accesskit/struct.ActionRequest.html) type for relaying user actions from assistive technology back to the application in a platform-independent way.
Adapters provide hooks for the application to be notified of action requests to be able to handle user actions.

## Servo accessibility for embedders

### `accessibility_enabled` pref

While the system is being developed, the [`accessibility_enabled`](https://doc.servo.org/servo/prefs/struct.Preferences.html#structfield.accessibility_enabled) pref must be set in order to enable the accessibility code to run.

### Activating accessibility for a `WebView`

The entry point for activating accessibility is [`WebView::set_accessibility_active()`](https://doc.servo.org/servo/webview/struct.WebView.html#method.set_accessibility_active).
This will return a randomly-generated `TreeId`, which will remain stable for the lifetime of the WebView.
The WebView's `TreeId` can also be accessed via the [`accesskit_tree_id()`](https://doc.servo.org/servo/webview/struct.WebView.html#method.accesskit_tree_id) method.

> [!IMPORTANT]
> The `WebView`'s `TreeId` _must_ be used to create a [graft node](#subtrees) in the embedder's application tree by sending a `TreeUpdate` to AccessKit Adapter including a node with a `tree_id` value corresponding to the WebView's `TreeId`, _before_ any `TreeUpdate`s are forwarded to AccessKit from the WebView.

<!--
This influenced our decision to change activation from a Servo method to a WebView method in [#43029](https://github.com/servo/servo/pull/43029).
-->

Once accessibility is active for the WebView, it will begin to emit `TreeUpdate`s via the [`WebViewDelegate::notify_accessibility_tree_update()`](https://doc.servo.org/servo/trait.WebViewDelegate.html#method.notify_accessibility_tree_update) method.
Once the graft node has been created, these `TreeUpdate`s can be forwarded directly to the AccessKit adapter.

The `WebView` will continue to emit `TreeUpdate`s for any change to its accessibility tree until either its `set_accessibility_active()` method is used to deactivate the accessibility tree, or its lifetime ends.
Accessibility tree changes will be triggered by navigations within the webview, as well as any changes to the currently active document.

Servo manages subtrees within the `WebView`'s accessibility tree; the embedder only needs to ensure that there is a graft node for the `WebView` in its top-level tree, and that Servo's `TreeUpdate`s are sent to the adapter in the order in which they are emitted from Servo.

![Diagram showing the data flow between the embedder, the WebView and accesskit as described above.](../images/embedder-accessibility-data-flow.svg)

> [!NOTE]
> The updates from the `WebView` are currently one-way: we don't yet support [`ActionRequest`](https://docs.rs/accesskit/latest/accesskit/struct.ActionRequest.html)s.

## WebView accessibility internals

As described in the [Servo accessibility for embedders](#servo-accessibility-for-embedders) section, the Servo accessibility system is exposed to embedders on a per-`WebView` basis.

The `WebView` has a [minimal tree](#webview-subtree) of its own, which essentially exists to provide a [graft node](#subtrees) for its top-level [`Pipeline`](https://doc.servo.org/servo_constellation/pipeline/struct.Pipeline.html)'s accessibility tree.

The tree for the pipeline is generated based on its document's structure by [layout::AccessibilityTree](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html).
This tree is created when accessibility is activated for the pipeline, and updated each time the document is reflowed.
Any changes to the tree are captured in a `TreeUpdate`, which is sent to the embedder.

> [!NOTE]
> We currently don't support accessibility trees in IFrames.

### WebView subtree

Each WebView has a minimal tree consisting of a [`ScrollView`](https://docs.rs/accesskit/0.24.0/accesskit/enum.Role.html#variant.ScrollView) and a graft node for the top-level pipeline (i.e. the top-level document).

A `TreeUpdate` with an updated graft node is emitted when accessibility is enabled for the WebView, and when the top-level pipeline (i.e. the top-level Document) changes.

![Diagram showing subtree grafting between the minimal tree for a WebView, containing just a ScrollView node and graft node, and the tree for a pipeline for a document named webpage.html](../images/servo-accessibility-webview-pipeline.svg)

### Accessibility activation

When an embedder calls `set_accessibility_active(true)` on a `WebView`, the `WebView` assumes responsibility for ensuring that until accessibility is deactivated or the `WebView` is destroyed, the embedder will receive `TreeUpdate`s representing the `WebView` and its current contents at any given time.

In order to do this, it needs to activate accessibility in its top-level [`Pipeline`](https://doc.servo.org/servo_constellation/pipeline/struct.Pipeline.html) both immediately, and whenever the top-level `Pipeline` changes.
It also de-activates accessibility in any inactive pipelines.

The basic initial flow is:

1. The embedder application calls [`set_accessibility_active(true)`](https://doc.servo.org/servo/webview/struct.WebView.html#method.set_accessibility_active) on the `WebView`.
    - This causes the `WebView` to randomly generate and store a `TreeId` for itself, which will remain consistent for the life of the `WebView` or until `set_accessibility_active(false)` is called.
2. The `WebView` sends a [`EmbedderToConstellationMessage::SetAccessibilityActive()`](https://doc.servo.org/servo_constellation_traits/enum.EmbedderToConstellationMessage.html#variant.SetAccessibilityActive) message to notify the constellation that accessibility should be activated for its top-level pipeline.
3. The constellation sends a [`ScriptThreadMessage::SetAccessibilityActive()`](https://doc.servo.org/script_traits/enum.ScriptThreadMessage.html#variant.SetAccessibilityActive) message to notify the script thread that accessibility should be activated for the specified pipeline.
4. The script thread calls [`set_accessibility_active()`](https://doc.servo.org/layout_api/trait.Layout.html#tymethod.set_accessibility_active) on the pipeline's [`LayoutThread`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html).
5. On the next reflow, the `LayoutThread` generates an initial `TreeUpdate` for its accessibility tree, and sends an [`EmbedderMsg::AccessibilityTreeUpdate()`](https://doc.servo.org/embedder_traits/enum.EmbedderMsg.html#variant.AccessibilityTreeUpdate) message with the tree update.
6. The `WebView` retrieves the `TreeUpdate`'s [`tree_id`](https://doc.servo.org/accesskit/struct.TreeUpdate.html#structfield.tree_id) and stores it in its [`grafted_accesskit_tree_id`](https://doc.servo.org/servo/webview/struct.WebViewInner.html#structfield.grafted_accesskit_tree_id) field.
   It then generates a `TreeUpdate` representing its own [minimal tree](#webview-subtree) with the [graft node](http://localhost:3000/design-documentation/accessibility.html#subtrees)'s `tree_id` set to the `grafted_accesskit_tree_id`, and passes that to its `WebViewDelegate`'s [`notify_accessibility_tree_update()`](https://doc.servo.org/servo/trait.WebViewDelegate.html#method.notify_accessibility_tree_update) method.
7. Once the graft node has been updated, the `WebView` can then call `notify_accessibility_tree_update()` again to forward the `TreeUpdate` from the pipeline.

After accessibility has been activated on the pipeline, it will continue to send `TreeUpdate`s to the `WebView`.
After the first, there's no need to send a separate `TreeUpdate` for the `WebView`'s tree; the `TreeUpdate`s from the pipeline can be passed directly to [`notify_accessibility_tree_update()`](https://doc.servo.org/servo/trait.WebViewDelegate.html#method.notify_accessibility_tree_update).

#### Handling navigations: grafted tree epoch

When there is a navigation, such as when a user enters a new URL in the address bar, clicks a link, or uses the back or forwards buttons, the `WebView`'s top-level pipeline changes.
This means that it needs to:

- de-activate accessibility in the old top-level pipeline,
- activate accessibility in the new top-level pipeline,
- graft the tree for the new pipeline in place of the tree for the old pipeline,
- begin forwarding the tree updates from the new pipeline, and
- **ignore** any further tree updates from the old pipeline.

We manage this by tracking an [Epoch](https://doc.servo.org/servo_base/struct.Epoch.html) which is incremented every time the top-level pipeline changes.
This epoch is passed from the Constellation, where the top-level pipeline is set, to [`ScriptThreadMessage::SetAccessibilityActive()`](https://doc.servo.org/script_traits/enum.ScriptThreadMessage.html#variant.SetAccessibilityActive) along with the `PipelineId`.
It's then sent back to the `WebView` in [`EmbedderMsg::AccessibilityTreeUpdate()`](https://doc.servo.org/embedder_traits/enum.EmbedderMsg.html#variant.AccessibilityTreeUpdate), and checked against its existing [`grafted_accesskit_tree_epoch`](https://doc.servo.org/servo/webview/struct.WebViewInner.html#structfield.grafted_accesskit_tree_epoch).

- If the epoch hasn't changed, the `TreeUpdate` can simply be forwarded to the embedder.
- If the epoch is greater than the existing [`grafted_accesskit_tree_epoch`](https://doc.servo.org/servo/webview/struct.WebViewInner.html#structfield.grafted_accesskit_tree_epoch), that indicates that a new tree needs to be grafted, and the epoch value needs to be updated.
- If the epoch is _less_ than the existing `grafted_accesskit_tree_epoch`, the `TreeUpdate` should be ignored.
  > [!IMPORTANT]
  > If the `TreeUpdate` with a stale epoch was forwarded to the embedder, it could cause a panic, as it would contain a `TreeId` which is no longer grafted in the `WebView`'s tree.


![Diagram showing activating accessibility and navigating to a new URL, illustrating the previous two sections.](../images/accessibility-activation.svg)

> [!NOTE]
> Deactivating accessibility in inactive pipelines means we destroy all of the cached accessibility tree information for that pipeline.
> This means that even if the user navigates in the [session history](https://doc.servo.org/servo_constellation/session_history/index.html), we will always need to re-compute all accessibility data whenever a navigation occurs.


### Deterministic `TreeId` generation for `Pipeline`s

<!--
[#43012](https://github.com/servo/servo/pull/43012)
-->

We have a deterministic mapping from a `PipelineId` to `accesskit::TreeId`, implemented using the [`Uuid::new_v5()`](https://docs.rs/uuid/latest/uuid/struct.Uuid.html#method.new_v5) method, using a static namespace value combined with the pipeline ID.

This was implemented to allow immediately sending a `TreeUpdate` updating the `WebView`'s graft node without needing to wait for a message to return from the pipeline.
However, now we update the graft node immediately after receiving the first `TreeUpdate` from the new pipeline, which also includes the tree id.

We expect it will be still useful when implementing IFrame support: we would only need to have the pipeline ID for the embedded frame to turn the `<iframe>` element into a graft node.

## Generating accessibility trees for web content: `layout::accessibility_tree`

We generate and update the accessibility tree for a single pipeline (i.e. a single web page being rendered) as part of the [reflow](https://doc.servo.org/layout_api/trait.Layout.html#tymethod.reflow) routine.
This allows us to ensure that all layout information is up to date before updating the accessibility tree, that the tree is updated whenever any DOM mutations and/or style recalculations have occurred, and that DOM mutations are prevented from occurring while the tree is being updated.

The logic for generating and updating the accessibility tree lives in [`layout::accessibility_tree`](https://doc.servo.org/layout/accessibility_tree/index.html).
This module includes:
- [`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html), representing the current state of the accessibility tree and the logic to update the tree based on the current document state
- [`AccessibilityNode`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityNode.html), representing a single node in the accessibility tree and the logic to update it based on its corresponding DOM node
- [`AccessibilityUpdate`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html), representing the in-process update pass, and providing the `TreeUpdate` when the update is complete.

Our goal is to make updating the accessibility tree fast enough that users can't notice any performance degradation when accessibility is active.

The accessibility tree lives in the `layout` crate because accessibility tree building depends on data from both the DOM tree and the outputs of layout.

### Activating accessibility for a pipeline

When the ScriptThread receives the `ScriptThreadMessage::SetAccessibilityActive` message for a pipeline, it locates the Document for that pipeline, and calls the [`set_accessibility_active()`](https://doc.servo.org/layout_api/trait.Layout.html#tymethod.set_accessibility_active) method on its `LayoutThread`.

This causes the `LayoutThread` to:
- toggle its [`accessibility_active`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.accessibility_active) flag,
- create an instance of [`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html) which is stored in its [`accessibility_tree`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.accessibility_tree) field, and
- set its [`needs_accessibility_update`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.needs_accessibility_update) flag, which marks it as needing the accessibility tree to be updated in the next reflow.

If no reflow is otherwise required, setting the `needs_accessibility_update` flag will ensure a rendering update occurs, as it is checked in Document's [`needs_rendering_update()`](https://doc.servo.org/script/dom/document/document/struct.Document.html#method.needs_rendering_update) method, and LayoutThread's [`can_skip_reflow_request_entirely()`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#method.can_skip_reflow_request_entirely) method.

When the next reflow occurs, if the LayoutThread's `accessibility_tree` exists, the accessibility tree update occurs as a phase after all the other phases in [`handle_reflow()`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#method.handle_reflow).
This primarily consists of calling the [`update_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) method on `AccessibilityTree`, which returns an [`accesskit::TreeUpdate`](https://doc.servo.org/accesskit/struct.TreeUpdate.html).

The `TreeUpdate` is emitted back to the embedder via [`EmbedderMessage::AccessibilityTreeUpdate`](https://doc.servo.org/servo/enum.EmbedderMsg.html#variant.AccessibilityTreeUpdate), where the `WebView` can forward it to the embedding application via [`WebViewDelegate::notify_accessibility_tree_update()`](https://doc.servo.org/servo/trait.WebViewDelegate.html#method.notify_accessibility_tree_update). (See [WebView accessibility internals](webview-accessibility-internals) for more information on how `TreeUpdate`s are processed in `WebView`.)

### `AccessibilityTree`

[`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html) represents the state of the accessibility tree as of the last reflow for a particular Document, and encapsulates the logic to update the tree based on the current document state and produce a `accesskit::TreeUpdate` which can be forwarded to embedders.

#### Updating the tree: `AccessibilityTree::update_tree()`

Each time a reflow occurs, `LayoutThread` will check its [`needs_accessibility_update`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.needs_accessibility_update) flag, and if it is set will call the [`update_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) method with the root node of the document.

`update_tree()` creates a new [`AccessibilityUpdate`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html) to track data relating to the update pass, updates its [`root_node_id`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#structfield.root_node_id) if necessary, and then calls into the recursive [update_node_and_descendants()](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_node_and_descendants).

#### `AccessibilityUpdate` and tree mutations

Methods in `AccessibilityTree` which can mutate the tree, such as [`get_or_create_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.get_or_create_node) and `remove_stale_nodes()`, take an `AccessibilityUpdate` in order to track what changes were made.

If an `AccessibilityNode` is changed in any way, it is added to the `AccessibilityUpdate`'s [`changed_nodes`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#structfield.changed_nodes) set.
This set is used to produce the `accesskit::TreeUpdate` when the `AccessibilityUpdate` is [finalized](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#method.finalize).

The `AccessibilityUpdate` also tracks what nodes have been added to, removed from and moved within the tree during the current update pass, in its [tree_changes](`https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#structfield.tree_changes`) map.
This map is consumed by the `AccessibilityTree::remove_stale_nodes()`.

Tree changes are determined based on updates to parent nodes:
- If a DOM node has a child which hasn't yet been added to the tree, that node will be created when [`get_or_create_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.get_or_create_node) is called, and it will be tracked as [`TreeChange::New`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.New)
- If a DOM node has a child which was previously the child of a different node, the child node will be tracked as [`TreeChange::PendingMove`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.PendingMove)
    - If it was previously tracked as `Removed`, it will be tracked as `Moved`
- If a DOM node *no longer* has a child which it had previously, that child node will be tracked as [`TreeChange::Removed`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.Removed)
    - If it was previously tracked as `PendingMove`, it will be tracked as `Moved`.

For a node to be tracked as [`Moved`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.Moved), it must be both removed from its old parent and added to its new parent in the same update pass, in either order.
When [tree_changes](`https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#structfield.tree_changes`) is processed during [finalization](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#method.finalize), any nodes with a `Removed` status will be deleted from the `AccessibilityTree`.
Any nodes which still have a `PendingMove` status at this point will cause a panic, as this would mean that they have been added to their new parent without being removed from their old parent.

#### Updating a single `AccessibilityNode`




```
// TODO: finish
```


## Servo accessibility tree testing

- Using the `accesskit_consumer` API to generate an in-memory tree from Servo `TreeUpdates`

```
// TODO: finish
```


## Servoshell accessibility tree integration

```
// TODO: write
```

# TODOs

- Adapters typically use accesskit_consumer to ingest tree updates; consumer can also be useful in other ways
    - Add section on `accesskit_consumer`?
- Future directions for testing
    - WebDriver methods
    - platform API testing using WPT integration (requires mapping DOM ID through to platform APIs which is not yet implemented in AccessKit)
- Link to PRs introducing various concepts?
    - Maybe just a standalone paragraph with the GitHub PR number as a link
