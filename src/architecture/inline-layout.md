# Inline Layout
In modern browsers inline layout consists from the following steps:
## Layout preparation
- Divide `BoxTree` into the set of subtree view objects that is called `Block Formatting Context` (`BFC`) and `Inline Formatting Context` (`IFC`); Plese do not confuse this termin with `Independent Formatiing Context` that also can be abbreviated as `IFC`.
- Accumulate all text within `Inline Formatting Context` into one `infinite string`(important to properly handle some abstractions that span across several hypertext markup elements - i.e. bidi directionality); Accumulate all elements with visual representation in `Inline Formatting Context` into container of `Inline Items`; During such aggregation html elements may introduce additional codepoints into string. In example some html elements under special conditions may setup independent `BIDI paragraph object` and to adress this fact it is necessary to introduce special `bidi-control symbols`.
- Then we need to prepare text for `shaping` procedure (the result of shaping is a size and position of each symbol that it will occupy within the string). **OpenType / TrueType specific preparation is described further**: During this process we split aquired infinite string into segments of consequative symbols that is sharing a set properties (same bidi-direction, font, language and script), and memorise such segments as `ranges` within original `infinite string`. For each generated `text segment` corresponding item must be introduced in `Inline Items` container.
- After we use some third party library that will actually extract information that is contained within font file
and perform `shaping`

## Layout
- The next procedure is LineBreaking: given an infinite string of symbols with known sizes and positions and foreign markup objects with known sizes that must be inserted into this infinite string string (`Atomic inlines`, `boxes of inline level elements`, e.t.c), distribute this set into several lines that will fit into constraints that parent `BlockLevel` `Box` imposes on `InlineFormatiingContext` (that procedure is unexpectedly tricky especially if floats is involved, if you need to modify it please thoroughly study existing solutions - especially token based linebreaking).
- After linebreaking we must perform `BIDI reordering` within the line and finally generate `Fragments` for each element within `IFC`. During this proceure we are working on `Inline Items` level. That means that text-direction may change the position of `box items` (visual representation of box borders) within the line.


## Detailed Explanation of steps:
### Inline Items construction
TODO
#### BIDI level computation
TODO
#### Font Style matching procedure
Exact details is provided in servo [fonts module](./fonts.md)

### Text Segmentation & Shaping
#### What is text shaping?
Wikipedia provides following definition:
> Text shaping is the process of converting text to glyph indices and positions as part of text rendering. It is complementary to font rendering as part of the text rendering process; font rendering is used to generate the glyphs, and text shaping decides which glyphs to render and where they should be put on the image plane. Unicode is generally used to specify the text to be rendered.

Microsoft have the following document that describe [Text layout](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout). It have section devoted to [Text shaping](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#text-shaping), however clear and short definition is not provided, this section names four important subtasks that any text shping engine must solve:
- [correct processing of ligatures](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#ligatures)
- [script-specific replacement of the characters that depends on context](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#contextual-shaping)
- [combining special characters (i.e diacritics and tone marks) into single visual representation](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#combining-characters)
- [script-specific (i.e Hindi, Devanagari) reordering of the characters](https://learn.microsoft.com/en-us/globalization/fonts-layout/text-layout#character-reordering)

[HarfBuzz definition](https://harfbuzz.github.io/what-is-harfbuzz.html) of text shaping:
> Text shaping is the process of translating a string of character codes (such as Unicode codepoints) into a properly arranged sequence of glyphs that can be rendered onto a screen or into final output form for inclusion in a document.

#### What facts everyone must know about text shaping:

First that everyone must know about font shaping is the fact that different shaping approaches exists. The two of which author is aware of is [SIL Graphite](https://graphite.sil.org/) and Opentype / TrueType shaping algorithms. Great writeup on both technologies provided by [article](https://graphite.sil.org/graphite_aboutOT.html) on the SIL Graphite website.
I also feel obliged to provide a link on [great repository](https://github.com/n8willis/opentype-shaping-documents) that contains a lot of documents regarding the OpenType / TrueType shaping.

Second most important thing that everyone must know is the fact that w3c established [Web Font Working Group](https://www.w3.org/groups/wg/webfonts/). That group created [WOFF fonts](https://www.w3.org/TR/WOFF/) to improve and standartized loading of fonts from web resources, mostly it contains the standart of data compression and additional headers for web straming. If we look at uncompressed font format we will find that it follows simmilar structure and shaping model as OpenType fonts. That means that OpenType shaping models is currently dominating web domain. So the rest of the information in the shaping section will be devoted to shaping operations specific to [OpenType / Truetype shaping models](https://harfbuzz.github.io/opentype-shaping-models.html).

#### OpenType / Truetype shaping model
It would be unreasonable to copy information about all different Opentype and Truetype shaping models here, so I will just provide the link to [awesome repository](https://github.com/n8willis/opentype-shaping-documents) about shaping again.

Now let's get to more practical side. For web engine developer it is not necessary to know every detail of notorious shaping process cause we are working with third-party crates that provide already written shaping engine. Here servo uses opensource HarfBuzz shaping engine written in C/C++ (if someone is intrested in writing pure Rust OpenType shaping engine, please consider to provide your implementation to servo authors). `harfbuzz-sys` crate is used as FFI between C/C++ implementation and Rust language.

HarfBuzz engine have special requirements to the inputs.
1. we must create special `hb_font_t` and `hb_face_t` structures. In our case creation of such structures is dictated by CSS styles. Users will define the font through CSS font-family and language; and face through combination of font-size, font-weight, font-style, font-stretch, ...
2. we must properly segment the whole text string accumulated in IFC to the segments of characters that share common properties (more details at [what harfbuzz doesn't do](https://harfbuzz.github.io/what-harfbuzz-doesnt-do.html)). List of properties provided bellow.

#### Text segment features that is shared by all codepoints
 - Bidi direction
 - Language
 - Script
 - ***Font*** (particular rigidly defined face within the font)

After segmentation we must provide set of OpenType features to the shaping engine.

### Inline items linebreaking
Unfortunately I don't have enough understanding of token based linebreaking algorithm to shrtly describe it here.
TODO

### Inline items BIDI Reordering
Bidi reordering should be preformed exactly as stated in [Unicode® Standard Annex #9 Unicode Bidirectional Algorithm](https://unicode.org/reports/tr9/).
Currently servo have only partial implementation of that algorithm.
Problems mostly concentrated at per-line reordering rules.
Rules [L1](https://unicode.org/reports/tr9/#L1)-[L4](https://unicode.org/reports/tr9/#L4) not properly implemented. For example we don't use information about bidi-paragraphs at all.

On conceptual level application developer should allways use icu4c or new pure rust icu crates for such operations.

### Line fragments generation
TODO

