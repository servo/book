<!-- TODO: needs copyediting -->

# Servo's style system overview

This document provides an overview of Servo's style system.
For more extensive details, refer to the [style doc comments][style-doc], or the [Styling Overview][wiki-styling-overview] in the wiki, which includes a conversation between Boris Zbarsky and Patrick Walton about how style sharing works.

<a name="selector-impl"></a>
## Selector Implementation

To ensure compatibility with Stylo (a project integrating Servo's style system into Gecko), selectors must be consistent.

The consistency is implemented in [selectors' SelectorImpl][selector-impl], containing the logic related to parsing pseudo-elements and other pseudo-classes apart from [tree-structural ones][tree-structural-pseudo-classes].

Servo extends the selector implementation trait in order to allow a few more things to be shared between Stylo and Servo.

The main Servo implementation (the one that is used in regular builds) is [SelectorImpl][servo-selector-impl].

<a name="dom-glue"></a>
## DOM glue

In order to keep DOM, layout and style in different modules, there are a few traits involved.

Style's [`dom` traits][style-dom-traits] (`TDocument`, `TElement`, `TNode`, `TRestyleDamage`) are the main "wall" between layout and style.

Layout's [`wrapper`][layout-wrapper] module makes sure that layout traits have the required traits implemented.

<a name="stylist"></a>
## The Stylist

The [`stylist`][stylist] structure holds all the selectors and device characteristics for a given document.

The stylesheets' CSS rules are converted into [`Rule`][selectors-rule]s.
They are then introduced in a [`SelectorMap`][selectors-selectormap] depending on the pseudo-element (see [`PerPseudoElementSelectorMap`][per-pseudo-selectormap]), stylesheet origin (see [`PerOriginSelectorMap`][per-origin-selectormap]), and priority (see the `normal` and `important` fields in [`PerOriginSelectorMap`][per-origin-selectormap]).

This structure is effectively created once per [pipeline][docs-pipeline], in the corresponding LayoutThread.

<a name="properties"></a>
## The `properties` module

The [properties module][properties-module] is a mako template.
Its complexity is derived from the code that stores properties, [`cascade` function][properties-cascade-fn] and computation logic of the returned value which is exposed in the main function.

[style-doc]: https://doc.servo.org/style/index.html
[wiki-styling-overview]: https://github.com/servo/servo/wiki/Styling-overview
[selector-impl]: https://doc.servo.org/selectors/parser/trait.SelectorImpl.html
[selector-impl-ext]: https://doc.servo.org/style/selector_parser/trait.SelectorImplExt.html
[servo-selector-impl]: https://doc.servo.org/style/servo/selector_parser/struct.SelectorImpl.html
[tree-structural-pseudo-classes]: https://www.w3.org/TR/selectors4/#structural-pseudos
[style-dom-traits]: https://doc.servo.org/style/dom/index.html
[layout-wrapper]: https://doc.servo.org/layout/wrapper/index.html
[stylist]: https://doc.servo.org/style/stylist/struct.Stylist.html
[selectors-selectormap]: https://doc.servo.org/style/selector_map/struct.SelectorMap.html
[selectors-rule]: https://doc.servo.org/style/stylist/struct.Rule.html
[per-pseudo-selectormap]: https://doc.servo.org/style/selector_parser/struct.PerPseudoElementMap.html
[per-origin-selectormap]: https://doc.servo.org/style/stylist/struct.PerOriginSelectorMap.html
[docs-pipeline]: https://github.com/servo/servo/blob/main/docs/glossary.md#pipeline
[properties-module]: https://doc.servo.org/style/properties/index.html
[properties-cascade-fn]: https://doc.servo.org/style/properties/fn.cascade.html
