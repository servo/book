# Inline Layout
## Foreword
Servo actually aims to provide the most up to date documentation along with the code, and Martin Robinson's comments to `components\layout_2020\flow\inline\mod.rs` file.
You can also find this in the form of [online crate documentation](https://doc.servo.org/layout/flow/inline/)
This writeup is already great but it misses some links to standards that actually responsible for the stage. Mostly Martin documentation explains module in the same way as [CSS Inline Layout Module Level 3, part 2, Inline Layout Model](https://www.w3.org/TR/css-inline-3/#model).
For that reason more detailed explanation of some steps procvided bellow.

## Specification that governs inline layout:
- [CSS Inline Layout Module Level 3](https://www.w3.org/TR/css-inline-3/)
- [CSS Text Module Level 4](https://www.w3.org/TR/css-text-4/)
- [CSS Writing Modes Level 4](https://www.w3.org/TR/css-writing-modes-4/)
- [CSS Logical Properties and Values Level 1](https://www.w3.org/TR/css-logical-1/)
- [CSS Fonts Module Level 4](https://www.w3.org/TR/css-fonts-4/)  
- [Unicode® Standard Annex #9 Unicode Bidirectional Algorithm](https://unicode.org/reports/tr9/)

## Some important documents
- [WHATWG Encodings](https://encoding.spec.whatwg.org/)
- [Character Model for the World Wide Web 1.0: Fundamentals](https://www.w3.org/TR/charmod/)
- [Migrating to Unicode](https://www.w3.org/International/articles/unicode-migration/)
- [Changing an HTML page to Unicode](https://www.w3.org/International/questions/qa-changing-encoding)
- [CSS Syntax Module Level 3, part 3, Tokenizing and Parsing CSS](https://www.w3.org/TR/css-syntax-3/#input-byte-stream)
- [How to use Unicode controls for bidi text](https://www.w3.org/International/questions/qa-bidi-unicode-controls)
- [Unicode Technical Report #36 Unicode Security Considerations](https://www.unicode.org/reports/tr36/)

# Inline Layout Steps
In modern browsers inline layout consists from the following steps:
## Before the Box tree
Text is the core data type for inline layout. And the very first step that may affect it visual representation happens on encoding detection and conversion on HTML and CSS parsing.

## Layout preparation
1. Divide `BoxTree` into the set of subtree view objects that is called `Block Formatting Context` (`BFC`) and `Inline Formatting Context` (`IFC`); Plese do not confuse this termin with `Independent Formatiing Context` that also can be abbreviated as `IFC`.
2. Accumulate all text within `Inline Formatting Context` into one `infinite string`(important to properly handle some abstractions that span across several hypertext markup elements - i.e. bidi directionality); Accumulate all elements with visual representation in `Inline Formatting Context` into container of `Inline Items`; During such aggregation html elements may introduce additional codepoints into string. In example some html elements under special conditions may setup independent `BIDI paragraph object` and to adress this fact it is necessary to introduce special `bidi-control symbols`.
3. Then we need to prepare text for `shaping` procedure (the result of shaping is a size and position of each symbol that it will occupy within the string). **OpenType / TrueType specific preparation is described further**: During this process we split aquired infinite string into segments of consequative symbols that is sharing a set properties (same bidi-direction, font, language and script), and memorise such segments as `ranges` within original `infinite string`. For each generated `text segment` corresponding item must be introduced in `Inline Items` container.
4. After we use some third party library that will actually extract information that is contained within font file
and perform `shaping`

## Layout
5. The next procedure is LineBreaking: given an infinite string of symbols with known sizes and positions and foreign markup objects with known sizes that must be inserted into this infinite string string (`Atomic inlines`, `boxes of inline level elements`, e.t.c), distribute this set into several lines that will fit into constraints that parent `BlockLevel` `Box` imposes on `InlineFormatiingContext` (that procedure is unexpectedly tricky especially if floats is involved, if you need to modify it please thoroughly study existing solutions - especially token based linebreaking).
6. After linebreaking we must perform `BIDI reordering` within the line and finally generate `Fragments` for each element within `IFC`. During this proceure we are working on `Inline Items` level. That means that bidi-direction may change the position of `inline box items` (visual representation of box borders) within the line. Also during the same stage we finally convert line logical coordinates to physical ones. Than means that CSS text-direction may apply additional rotations that will affect final position of the framents.


## Detailed Explanation of steps:
### Inline Items construction
The code for this step can be found at:
`components\layout_2020\flow\inline\construct.rs`.
If `block-level` element have some text, or non collapsable space inside we start to traverse children of such element within `Box-tree` and create special helping structures that will be used on the following steps.
```rust
pub(crate) enum InlineItem {
    StartInlineBox(ArcRefCell<InlineBox>),
    EndInlineBox,
    TextRun(ArcRefCell<TextRun>),
    OutOfFlowAbsolutelyPositionedBox(
        ArcRefCell<AbsolutelyPositionedBox>,
        usize, /* offset_in_text */
    ),
    OutOfFlowFloatBox(Arc<FloatBox>),
    Atomic(
        Arc<IndependentFormattingContext>,
        usize, /* offset_in_text */
        Level, /* bidi_level */
    ),
}
```

#### BIDI level computation
Bidi reordering should be preformed exactly as stated in [Unicode® Standard Annex #9 Unicode Bidirectional Algorithm, point 3.3 Resolving Embedding Levels](https://unicode.org/reports/tr9/#Resolving_Embedding_Levels).

On conceptual level, application developer in most cases should use icu4c or new pure rust icu crates for such operations. However as for now, all realizations do not provide interfaces to add external markup elements into bidi resolution procedure.

Currently servo uses `unicode-bidi` crate and introduced some heuristic to determin bidi-levels of the rest of inline-items:
`components\layout_2020\flow\inline\mod.rs`
```rust
impl InlineFormattingContext {
    #[cfg_attr(
        feature = "tracing",
        tracing::instrument(
            name = "InlineFormattingContext::new_with_builder",
            skip_all,
            fields(servo_profiling = true),
            level = "trace",
        )
    )]
    pub(super) fn new_with_builder(
        builder: InlineFormattingContextBuilder,
        layout_context: &LayoutContext,
        propagated_data: PropagatedBoxTreeData,
        has_first_formatted_line: bool,
        is_single_line_text_input: bool,
        starting_bidi_level: Level,
    ) -> Self {
        // This is to prevent a double borrow.
        let text_content: String = builder.text_segments.into_iter().collect();
        let mut font_metrics = Vec::new();

        let bidi_info = BidiInfo::new(&text_content, Some(starting_bidi_level));
        ...
    }
    ...
}
```
`components\layout_2020\flow\inline\line.rs`
```rust
    pub(super) fn layout(&mut self, mut line_items: Vec<LineItem>) -> Vec<Fragment> {
        let mut last_level = Level::ltr();
        let levels: Vec<_> = line_items
            .iter()
            .map(|item| {
                let level = match item {
                    LineItem::TextRun(_, text_run) => text_run.bidi_level,
                    // TODO: This level needs either to be last_level, or if there were
                    // unicode characters inserted for the inline box, we need to get the
                    // level from them.
                    LineItem::InlineStartBoxPaddingBorderMargin(_) => last_level,
                    LineItem::InlineEndBoxPaddingBorderMargin(_) => last_level,
                    LineItem::Atomic(_, atomic) => atomic.bidi_level,
                    LineItem::AbsolutelyPositioned(..) => last_level,
                    LineItem::Float(..) => {
                        // At this point the float is already positioned, so it doesn't really matter what
                        // position it's fragment has in the order of line items.
                        last_level
                    },
                };
                last_level = level;
                level
            })
            .collect();
        ...
    }
```
Current realization is not perfect and leads to several bugs on WPT tests, that reader of this document may try to solve. Bugs not necesary related to [BIDI level computation](#bidi-level-computation) and may also stem from [Inline items BIDI Reordering](#inline-items-bidi-reordering)
- [wpt/css/CSS2/bidi-text](https://wpt.fyi/results/css/CSS2/bidi-text?label=master&product=chrome%5Bexperimental%5D&product=edge%5Bexperimental%5D&product=firefox%5Bexperimental%5D&product=safari%5Bexperimental%5D&product=servo&aligned)
- [css/CSS2/text/bidi-flag-emoji](https://wpt.fyi/results/css/CSS2/text/bidi-flag-emoji.html?label=master&product=chrome%5Bexperimental%5D&product=edge%5Bexperimental%5D&product=firefox%5Bexperimental%5D&product=safari%5Bexperimental%5D&product=servo&aligned)
- [css/CSS2/text/bidi-span-003](https://wpt.fyi/results/css/CSS2/text/bidi-span-003.html?label=master&product=chrome%5Bexperimental%5D&product=edge%5Bexperimental%5D&product=firefox%5Bexperimental%5D&product=safari%5Bexperimental%5D&product=servo&aligned)
- ...

#### Font Style matching procedure
Exact details is provided in servo [fonts module](./fonts.md)

### Text Segmentation & Shaping
#### What is text shaping?
Different sources create different terms: [Wikipedia definition](https://en.wikipedia.org/wiki/Text_shaping), [HarfBuzz definition](https://harfbuzz.github.io/what-is-harfbuzz.html)

Microsoft have the following document [Text layout](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout). It have section devoted to [Text shaping](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#text-shaping), however clear and short definition is not provided, this section names four important subtasks that any text shping engine must solve:
- [correct processing of ligatures](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#ligatures)
- [script-specific replacement of the characters that depends on context](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#contextual-shaping)
- [combining special characters (i.e diacritics and tone marks) into single visual representation](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#combining-characters)
- [script-specific (i.e Hindi, Devanagari) reordering of the characters](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#character-reordering)

#### What facts everyone must know about text shaping:

First, different shaping approaches exists. The two of which author is aware of is [SIL Graphite](https://graphite.sil.org/) and Opentype / TrueType shaping algorithms. Great writeup on both technologies provided by [article](https://graphite.sil.org/graphite_aboutOT.html) on the SIL Graphite website.
I also feel obliged to provide a link on [great repository](https://github.com/n8willis/opentype-shaping-documents) that contains a lot of documents regarding the OpenType / TrueType shaping.

Second, w3c established [Web Font Working Group](https://www.w3.org/groups/wg/webfonts/). That group created [WOFF fonts](https://www.w3.org/TR/WOFF/) to improve and standartized loading of fonts from web resources, mostly it contains the standart of data compression and additional headers for web straming. If we look at uncompressed font format we will find that it follows simmilar structure and shaping model as OpenType fonts. That means that OpenType shaping models is currently standart one in the web domain. Rest of the information in the shaping section will be devoted to shaping operations specific to [OpenType / Truetype shaping models](https://harfbuzz.github.io/opentype-shaping-models.html).

#### OpenType / Truetype shaping model
It would be unreasonable to copy information about all different Opentype and Truetype shaping models here, so I will just provide the link to [awesome repository](https://github.com/n8willis/opentype-shaping-documents) about shaping again.

Now let's get to more practical side. For web engine developer it is not necessary to know every detail of notorious shaping process cause we are working with third-party crates that provide already written shaping engine. Here servo uses opensource HarfBuzz shaping engine written in C/C++ (if someone is intrested in writing pure Rust OpenType shaping engine, please consider to provide your implementation to servo authors). `harfbuzz-sys` crate is used as FFI between C/C++ implementation and Rust language.

HarfBuzz engine have special requirements to the inputs.
1. we must create special `hb_font_t` and `hb_face_t` structures. In our case creation of such structures is dictated by CSS styles. Users will define the font through CSS font-family and language; and face through combination of font-size, font-weight, font-style, font-stretch, ... Also special input output structure called `hb_buffer` must be created.
2. we must properly segment the whole text string accumulated in IFC to the segments of characters that share common properties (more details at [what harfbuzz doesn't do](https://harfbuzz.github.io/what-harfbuzz-doesnt-do.html)). List of properties provided bellow.

#### Text segment features that is shared by all codepoints
 - Bidi direction
 - Language
 - Script
 - ***Font*** (particular rigidly defined face within the font)

After segmentation we must provide set of OpenType features to the shaping engine.
Web specifications have [default set of Opentype features](https://www.w3.org/TR/css-fonts-4/#default-features) that must allways be enabled. The only situation when this is not uphold is when user explicitely disable some features, i.e. when CSS `font-variant-ligatures` is set to `no-common-ligatures`.

Now all that is left is to provide all created data to `hb_shape` function call (`hb_font`, `features` vector, `hb_buffer`).
We will call `hb_shape` for each text_segment that we determined on previous steps.
For each segment we must create special `hb_font` service object with help of information that was provided by platform font manager (MacOS: `Core Text`; Windows: `Direct Write`; Unix: `Fontconfig + Freetype2`; Openharmony and Android currently use Freetype2 in a hacky way).
We must populate special `hb_buffer` structure with the set of characters that belongs to the segment that we want shape.
After the call to `hb_shape` we extract information about sizes and positions of each character within the shaped segment from same `hb_buffer` structure that we used as input.


### Inline items linebreaking
Unfortunately I don't have enough understanding of token based linebreaking algorithm to shortly describe it here.
TODO higlight most important and non trivial steps of algorithm

### Inline items BIDI Reordering
Bidi reordering should be preformed exactly as stated in [Unicode® Standard Annex #9 Unicode Bidirectional Algorithm, point 3.4 Reordering Resolved Levels](https://unicode.org/reports/tr9/#Reordering_Resolved_Levels).
Currently servo have only partial implementation of that algorithm.
Problems mostly concentrated at per-line reordering rules.
Rules [L1](https://unicode.org/reports/tr9/#L1)-[L4](https://unicode.org/reports/tr9/#L4) not properly implemented. For example we don't use information about bidi-paragraphs at all.

On conceptual level, application developer should allways use icu4c or new pure rust icu crates for such operations.

### Line fragments generation
TODO higlight most important and non trivial steps of algorithm

