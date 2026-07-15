# Generating accessibility trees for web content: `layout::accessibility_tree`

We generate and update the accessibility tree for a single pipeline (i.e. a single web page being rendered) as part of the [reflow](https://doc.servo.org/layout_api/trait.Layout.html#tymethod.reflow) routine.
This allows us to ensure that all layout information is up to date before updating the accessibility tree, that the tree is updated whenever any DOM mutations and/or style recalculations have occurred, and that DOM mutations are prevented from occurring while the tree is being updated.

The logic for generating and updating the accessibility tree lives in [`layout::accessibility_tree`](https://doc.servo.org/layout/accessibility_tree/index.html).
This module includes:
- [`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html), representing the current state of the accessibility tree and the logic to update the tree based on the current document state
- [`AccessibilityNode`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityNode.html), representing a single node in the accessibility tree and the logic to update it based on its corresponding DOM node
- [`AccessibilityUpdate`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html), representing the in-progress update pass, and yielding the `TreeUpdate` when the update is complete.

Our aspirational goal is to make updating the accessibility tree fast enough that users won't notice any performance degradation when accessibility is active.

The accessibility tree lives in the `layout` crate because accessibility tree building depends on data from both the DOM tree and the outputs of layout.

## Activating accessibility for a pipeline

When the ScriptThread receives the `ScriptThreadMessage::SetAccessibilityActive` message for a pipeline, it locates the Document for that pipeline, and calls the [`set_accessibility_active()`](https://doc.servo.org/layout_api/trait.Layout.html#tymethod.set_accessibility_active) method on its `LayoutThread`.

This causes the `LayoutThread` to:
- toggle its [`accessibility_active`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.accessibility_active) flag,
- create an instance of [`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html) which is stored in its [`accessibility_tree`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.accessibility_tree) field, and
- set its [`needs_accessibility_update`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.needs_accessibility_update) flag, which marks it as needing the accessibility tree to be updated in the next reflow.

Even if no reflow is otherwise required, setting the `needs_accessibility_update` flag will ensure a rendering update occurs, as it is checked in Document's [`needs_rendering_update()`](https://doc.servo.org/script/dom/document/document/struct.Document.html#method.needs_rendering_update) method, and LayoutThread's [`can_skip_reflow_request_entirely()`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#method.can_skip_reflow_request_entirely) method.

For example, if you loaded a static web page in `servoshell`, waited until the load and rendering the page were complete, and then started an assistive technology to activate accessibility, this would ensure that layout would run even though there would otherwise be no reason to run layout.
That ensures the accessibility tree will be populated regardless of whether a layout is required otherwise.

When the next reflow occurs, if the LayoutThread's `accessibility_tree` exists, the accessibility tree update occurs as a phase after all the other phases in [`handle_reflow()`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#method.handle_reflow).
This primarily consists of calling the [`update_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) method on `AccessibilityTree`, which returns an [`accesskit::TreeUpdate`](https://doc.servo.org/accesskit/struct.TreeUpdate.html).

The `TreeUpdate` is emitted back to the embedder via [`EmbedderMessage::AccessibilityTreeUpdate`](https://doc.servo.org/servo/enum.EmbedderMsg.html#variant.AccessibilityTreeUpdate), where the `WebView` can forward it to the embedding application via [`WebViewDelegate::notify_accessibility_tree_update()`](https://doc.servo.org/servo/trait.WebViewDelegate.html#method.notify_accessibility_tree_update). (See [WebView accessibility internals](webview-internals.md) for more information on how `TreeUpdate`s are processed in `WebView`.)

## `AccessibilityTree`

[`AccessibilityTree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html) represents the state of the accessibility tree as of the last reflow for a particular Document, and encapsulates the logic to update the tree based on the current document state and produce an `accesskit::TreeUpdate` which can be forwarded to embedders.

### Updating the tree: `AccessibilityTree::update_tree()`

Each time a reflow occurs, `LayoutThread` will check its [`needs_accessibility_update`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.needs_accessibility_update) flag, and if it is set will call the [`update_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) method on its [`accessibility_tree`](https://doc.servo.org/layout/layout_impl/struct.LayoutThread.html#structfield.accessibility_tree).

`update_tree()` creates a new [`AccessibilityUpdate`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html) to track data relating to the update pass, updates its [`root_node_id`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#structfield.root_node_id) if necessary, and then updates itself based on data from the DOM.

### `AccessibilityUpdate`

Methods in `AccessibilityTree` which can mutate the tree, such as [`get_or_create_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.get_or_create_node) and `drop_removed_nodes()`, take an `AccessibilityUpdate` in order to track what changes were made.

If an `AccessibilityNode` is changed in any way, it is added to the `AccessibilityUpdate`'s [`changed_nodes`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#structfield.changed_nodes) set.
This set is used to produce the `accesskit::TreeUpdate` when the `AccessibilityUpdate` is [finalized](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#method.finalize).

### Initial tree construction

The first time [`update_tree`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) is called on the accessibility tree, its [`nodes`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#structfield.nodes) map is empty and needs to be populated from the DOM tree.
This will produce an initial `accesskit::TreeUpdate` to populate the tree on the AccessKit side.

[`ensure_root_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.ensure_root_node) will create the root node for the accessibility tree based on the root DOM node.
Since the root node is newly created, its corresponding DOM node gets pushed into the `damage_from_dom` structure with [`AccessibilityDamage::Rebuild`](https://doc.servo.org/layout_api/layout_damage/struct.AccessibilityDamage.html#associatedconstant.Rebuild), ensuring it will be completely populated from the DOM tree, including populating its children.

[`apply_changes_from_dom_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.apply_changes_from_dom_tree) takes the `damage_from_dom` structure with the root DOM node marked as `Rebuild` (and potentially other DOM nodes marked with various damage, although since all nodes will be newly created any damage from the DOM tree is irrelevant).
This method will then call into [`update_node_and_descendants_from_dom_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_node_and_descendants_from_dom_node) for the root node.

[`update_node_and_descendants_from_dom_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_node_and_descendants_from_dom_node) populates the root node in two steps:
- First [`AccessibilityNode::update_node_from_dom_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityNode.html#method.update_node_from_dom_node) populates the node's local properties, such as its role.
- Second, [`AccessibilityNode::update_descendants_from_dom_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityNode.html#method.update_descendants_from_dom_node) populates the node's children - recursively calling into `AccessibilityTree::update_node_and_descendants_from_dom_node()` for each new child.

Some properties of accessibility nodes, such as some nodes' [computed names](https://www.w3.org/TR/accname-1.2/), are dependent on other information in the accessibility tree and can only be computed after that information is populated from the DOM tree.
We track changes to nodes which may cause these properties to need recomputation by tracking propagating [`LocalAccessibilityDamage`](https://doc.servo.org/layout/accessibility_tree/struct.LocalAccessibilityDamage.html) within the tree.
"Local" in this context differentiates this type of damage from [`AccessibilityDamage`](https://doc.servo.org/layout_api/layout_damage/struct.AccessibilityDamage.html) which comes from the DOM tree.
As the tree is populated from the DOM tree via `update_node_and_descendants_from_dom_node()`, the `AccessibilityUpdate` keeps track of any [`LocalAccessibilityDamage`](https://doc.servo.org/layout/accessibility_tree/struct.LocalAccessibilityDamage.html) for each node.
After the updates from the DOM tree have finished, `LocalAccessibilityDamage` is propoagated within the tree.
Finally, `LocalAccessibilityDamage` tracked in the `AccessibiltyUpdate` is consumed in [`AccessibilityTree::resolve_local_damage_for_node_and_subtree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.resolve_local_damage_for_node_and_subtree), starting from the root node.
This method first calls into [`AccessibilityNode::update_node_local()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityNode.html#method.update_node_local) to resolve the local damage on the node, and then recurses into the node's children if necessary.

Finally, after these three update phases (creating the root node, populating it recursively from the DOM tree, and computing properties which are based on the populated accessibility tree) are complete, the `AccessibilityUpdate` is [`finalize()`d](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#method.finalize), producing the initial `accesskit::TreeUpdate` for the tree.

### Incremental updates

Calls to [`update_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.update_tree) after the tree has been populated for the first time follow the same basic flow, but with differences resulting from the tree already being populated.

Typically, calls to `ensure_root_node()` after the tree has been populated will essentially be a no-op, since there will already be a node associated with the root DOM node.

The `damage_from_dom` argument to `update_tree()` should now contain pairs of corresponding `ServoLayoutNode`s and `AccessibilityDamage` values.
These are collected in between reflows on the Document's [`AccessibilityData`](https://doc.servo.org/script/dom/document/accessibility_data/struct.AccessibilityData.html), and passed in to the reflow method via [`ReflowRequest`](https://doc.servo.org/layout_api/struct.ReflowRequest.html#structfield.accessibility_damage).

The `damage_from_dom` structure is passed (as previously) to [`apply_changes_from_dom_tree()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.apply_changes_from_dom_tree), where it now allows us to update only nodes whose corresponding DOM nodes have changed since the last tree update.
Any nodes which have been added to the DOM tree since the last accessibility update will be picked up due to a parent node having a [`Children`](https://doc.servo.org/layout_api/struct.AccessibilityDamage.html#associatedconstant.Children) damage value; from there, any new nodes will be populated recursively the same way the root node is in the initial update.

### Dropping nodes from the `AccessibilityTree`: `TreeChange`

Once the tree update is complete, any `AccessibilityNode` which is no longer in the tree is dropped.
This happens in the [`AccessibilityTree::drop_removed_nodes()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.drop_removed_nodes) method, which consumes parts of the `AccessibilityUpdate` during `finalize()`.
`drop_removed_nodes()` is called at the end of the update so that we can distinguish between a node which has been removed from its parent node because it was moved elsewhere in the tree, and a node which has been removed from the tree altogether.

We determine which nodes to drop using the `AccessibilityUpdate`'s [`tree_changes`](`https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#structfield.tree_changes`) map, which tracks what nodes have been added to, removed from and moved within the tree during the current update pass.

Tree changes are determined based on updates to parent nodes:
- If a DOM node has a child which hasn't yet been added to the tree, that node will be created when [`get_or_create_node()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.get_or_create_node) is called, and it will be tracked as [`TreeChange::New`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.New)
    - A node which is `New` in a particular update can never be `Moved` or `Removed` in the same update.
- If a DOM node has a child which was previously the child of a different node, the child node will be tracked as [`TreeChange::PendingMove`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.PendingMove), or `Moved` if it was previously tracked as `Removed`.
- If a DOM node *no longer* has a child which it had previously, that child node will be tracked as [`TreeChange::Removed`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.Removed), or `Moved` if it was previously tracked as `PendingMove`.

For a node to be tracked as [`Moved`](https://doc.servo.org/layout/accessibility_tree/enum.TreeChange.html#variant.Moved), it must be both removed from its old parent and added to its new parent in the same update pass, in either order.

When [tree_changes](`https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#structfield.tree_changes`) is processed by [`AccessibilityTree::drop_removed_nodes()`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#method.drop_removed_nodes) during [finalization](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityUpdate.html#method.finalize), any nodes in the subtree of a node with `Removed` status will be dropped from the tree's [`nodes`](https://doc.servo.org/layout/accessibility_tree/struct.AccessibilityTree.html#structfield.nodes).
Any nodes which still have a `PendingMove` status at this point will cause a panic, as this would mean that they have been added to their new parent without being removed from their old parent.

### (TODO) Ensuring `AccessibilityNode`s don't outlive their corresponding DOM nodes

```
// TODO: write
```

<!-- Rooting nodes in AccessibilityData -->

