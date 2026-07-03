# Generating accessibility trees for web content: `layout::accessibility_tree`

We generate and update the accessibility tree for a single pipeline (i.e. a single web page being rendered) as part of the [reflow](https://doc.servo.org/layout_api/trait.Layout.html#tymethod.reflow) routine.
This allows us to ensure that all layout information is up to date before updating the accessibility tree, that the tree is updated whenever any DOM mutations and/or style recalculations have occurred, and that DOM mutations are prevented from occurring while the tree is being updated.

The logic for generating and updating the accessibility tree lives in [`layout::accessibility_tree`](https://doc.servo.org/layout/accessibility_tree/index.html).
This module includes:
- [`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html), representing the current state of the accessibility tree and the logic to update the tree based on the current document state
- [`AccessibilityNode`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityNode.html), representing a single node in the accessibility tree and the logic to update it based on its corresponding DOM node
- [`AccessibilityUpdate`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html), representing the in-process update pass, and providing the `TreeUpdate` when the update is complete.

Our goal is to make updating the accessibility tree fast enough that users can't notice any performance degradation when accessibility is active.

The accessibility tree lives in the `layout` crate because accessibility tree building depends on data from both the DOM tree and the outputs of layout.

## Activating accessibility for a pipeline

When the ScriptThread receives the `ScriptThreadMessage::SetAccessibilityActive` message for a pipeline, it locates the Document for that pipeline, and calls the [`set_accessibility_active()`](https://doc.servo.org/layout_api/trait.Layout.html#tymethod.set_accessibility_active) method on its `LayoutThread`.

This causes the `LayoutThread` to:
- toggle its [`accessibility_active`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.accessibility_active) flag,
- create an instance of [`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html) which is stored in its [`accessibility_tree`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.accessibility_tree) field, and
- set its [`needs_accessibility_update`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.needs_accessibility_update) flag, which marks it as needing the accessibility tree to be updated in the next reflow.

If no reflow is otherwise required, setting the `needs_accessibility_update` flag will ensure a rendering update occurs, as it is checked in Document's [`needs_rendering_update()`](https://doc.servo.org/script/dom/document/document/struct.Document.html#method.needs_rendering_update) method, and LayoutThread's [`can_skip_reflow_request_entirely()`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#method.can_skip_reflow_request_entirely) method.

When the next reflow occurs, if the LayoutThread's `accessibility_tree` exists, the accessibility tree update occurs as a phase after all the other phases in [`handle_reflow()`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#method.handle_reflow).
This primarily consists of calling the [`update_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) method on `AccessibilityTree`, which returns an [`accesskit::TreeUpdate`](https://doc.servo.org/accesskit/struct.TreeUpdate.html).

The `TreeUpdate` is emitted back to the embedder via [`EmbedderMessage::AccessibilityTreeUpdate`](https://doc.servo.org/servo/enum.EmbedderMsg.html#variant.AccessibilityTreeUpdate), where the `WebView` can forward it to the embedding application via [`WebViewDelegate::notify_accessibility_tree_update()`](https://doc.servo.org/servo/trait.WebViewDelegate.html#method.notify_accessibility_tree_update). (See [WebView accessibility internals](webview-accessibility-internals) for more information on how `TreeUpdate`s are processed in `WebView`.)

## `AccessibilityTree`

[`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html) represents the state of the accessibility tree as of the last reflow for a particular Document, and encapsulates the logic to update the tree based on the current document state and produce a `accesskit::TreeUpdate` which can be forwarded to embedders.

### Updating the tree: `AccessibilityTree::update_tree()`

Each time a reflow occurs, `LayoutThread` will check its [`needs_accessibility_update`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.needs_accessibility_update) flag, and if it is set will call the [`update_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) method with the root node of the document.

`update_tree()` creates a new [`AccessibilityUpdate`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html) to track data relating to the update pass, updates its [`root_node_id`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#structfield.root_node_id) if necessary, and then calls into the recursive [update_node_and_descendants()](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_node_and_descendants).

### `AccessibilityUpdate` and tree mutations

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

### Updating a single `AccessibilityNode`




```
// TODO: finish
```
