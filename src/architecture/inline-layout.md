# Inline Layout
In modern browsers inline layout consists form the following steps:
## Layout preparation
- Divide `BoxTree` into the set of subtree view objects that is called `Block Formatting Context` (`BFC`) and `Inline Formatting Context` (`IFC`); Plese do not confuse this termin with `Independent Formatiing Context` that also can be abbreviated as `IFC`.
- Accumulate all text within `Inline Formatting Context` inside one `infinite string`; Accumulate all elements with visual representation in `Inline Formatting Context` into container of `Inline Items`; During such aggregation html elements may introduce additional codepoints into string. In example some html elements under special conditions may setup independent `BIDI paragraph object` and to adress this fact it is necessary to introduce special `bidi-control symbols`.
- Then we need to prepare text for `shaping` procedure (the result of shaping is a size and position of each symbol that it will occupy within the string). **OpenType / TrueType specific preparation is described further**: During this process we split aquired infinite string into segments of consequative symbols that is sharing a set properties (same bidi-direction, font, language and script), and memorise such segments as `ranges` within original `infinite string`. For each generated `text segment` corresponding item must be introduced in `Inline Items` container.
- After we use some third party library that will actually extract information that is contained within font file
and perform `shaping`

## Layout
- The next procedure is LineBreaking: given an infinite string of symbols with known sizes and positions and foreign markup objects with known sizes that must be inserted into this infinite string string (`Atomic inlines`, `boxes of inline level elements`, e.t.c), distribute this set into several lines that will fit into constraints that parent `BlockLevel` `Box` imposes on `InlineFormatiingContext` (that procedure is unexpectedly tricky especially if floats is involved, if you need to modify it please thoroughly study existing solutions - especially token based linebreaking).
- After linebreaking we must perform `BIDI reordering` within the line and finally generate `Fragments` for each element within `IFC`. During this proceure we are working on `Inline Items` level. That means that text-direction may change the position of `box items` (visual representation of box borders) within the line.


## Detailed Explanation of steps:
### Inline Items construction
TODO
### Text Segmentation
TODO
#### BIDI level computation
TODO
#### Font Style matching procedure
TODO
### Shaping
TODO

