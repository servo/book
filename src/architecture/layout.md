<!-- TODO: needs copyediting -->

# Layout

Servo's current layout system is known as Layout 2020. It [supersedes](https://github.com/servo/servo/wiki/Servo-Layout-Engines-Report) the now-removed original layout system.

Layout happens in three phases: box tree construction, fragment tree construction, and display list construction.
Once a display list is generated, it is sent to [WebRender](https://github.com/servo/webrender) for rendering.
When possible during tree construction, layout will try to use parallelism with Rayon.
Certain CSS feature prevent parallelism such as floats or counters.
The same code is used for both parallel and serial layout.

## Box Tree

The *box tree* is tree that represents the nested formatting contexts as described in the [CSS specification][formatting-context].
There are various kinds of formatting contexts, such as block formatting contexts (for block flow), inline formatting contexts (for inline flow), table formatting contexts, and flex formatting contexts.
Each formatting context has different rules for how boxes inside that context are laid out.
Servo represents this tree of contexts using nested enums, which ensure that the content inside each context can only be the sort of content described in the specification.

The box tree is just the initial representation of the layout state and generally speaking the next phase is to run the layout algorithm on the box tree and produce a fragment tree.
Fragments in CSS are the results of splitting elements in the box tree into multiple fragments due to things like line breaking, columns, and pagination.
Additionally during this layout phase, Servo will position and size the resulting fragments relative to their containing blocks.
The transformation generally takes place in a function called `layout(...)` on the different box tree data structures.

Layout of the *box tree* into the *fragment tree* is done in parallel, until a section of the tree with floats is encountered.
In those sections, a sequential pass is done and parallel layout can commence again once the layout algorithm moves across the boundaries of the block formatting context that contains the floats, whether by descending into an independent formatting context or finishing the layout of the float container.

[formatting-context]: https://drafts.csswg.org/css-display/#formatting-context

## Fragment Tree

The product of the layout step is a *fragment tree*.
In this tree, elements that were split into different pieces due to line breaking, columns, or pagination have a fragment for every piece.
In addition, each fragment is positioned relatively to a fragment corresponding to its containing block.
For positioned fragments, an extra placeholder fragment, `AbsoluteOrFixedPositioned`, is left in the original tree position.
This placeholder is used to build the display list in the proper order according the CSS painting order.

## Display List Construction

Once layout has created a *fragment tree*, it can move on to the next phase of rendering which is to produce a display list for the tree.
During this phase, the *fragment tree* is transformed into a [WebRender](https://github.com/servo/webrender) display list which consists of display list items (rectangles, lines, images, text runs, shadows, etc).
WebRender does not need a large variety of display list items to represent web content.

In addition to normal display list items, WebRender also uses a tree of *spatial nodes* to represent transformations, scrollable areas, and sticky content.
This tree is essentially a description of how to apply post-layout transformations to display list items.
When the page is scrolled, the offset on the root scrolling node can be adjusted without immediately doing a layout.
Likewise, WebRender has the capability to apply transformations, including 3D transformations to web content with a type of spatial node called a *reference frame*.

Clipping whether from CSS clipping or from the clipping introduced by the CSS `overflow` property is handled by another tree of *clip nodes*.
These nodes also have *spatial nodes* assigned to them so that clips stay in sync with the rest of web content.
WebRender decides how best to apply a series of clips to each item.

Once the display list is constructed it is sent to the compositor which forwards it to WebRender.
