# TODO: wiki/Design

<!-- https://github.com/servo/servo/wiki/Design/0941531122361aac8c88d582aa640ec689cdcdd1 -->

Servo is a project to develop a new Web browser engine. Our goal is to create an architecture that takes advantage of parallelism at many levels while eliminating common sources of bugs and security vulnerabilities associated with incorrect memory management and data races.

Because C++ is poorly suited to preventing these problems, Servo is written in [Rust](http://rust-lang.org), a new language designed specifically with Servo's requirements in mind. Rust provides a task-parallel infrastructure and a strong type system that enforces memory safety and data race freedom.

When making design decisions we will prioritize the features of the modern web platform that are amenable to high-performance, dynamic, and media-rich applications, potentially at the cost of features that cannot be optimized. We want to know what a fast and responsive web platform looks like, and to implement it.

## Architecture

```mermaid
flowchart TB
    subgraph Content Process
    ScriptA[Script Thread A]-->LayoutA[Layout A]
    LayoutA
    ScriptB[Script Thread B]-->LayoutB
    LayoutB[Layout B]
    end

    subgraph Main Process
    direction TB
    Embedder-->Constellation[Constellation Thread]
    Embedder<-->Compositor[Compositor]
    Constellation<-->Compositor
    Compositor-->WebRender
    Constellation-->Font[Font Cache]
    Constellation-->Image[Image Cache]
    Constellation-->Resource[Resource Manager]
    end

    Constellation<-->ScriptA
    LayoutA-->Image
    LayoutA-->Font
    LayoutA-->Compositor
 ```

This diagram shows the architecture of Servo in the case of only a single content process. Servo is designed to support multiple content processes at once. A single content process can have multiple script threads running at the same time with their own layout. These have their own communication channels with the main process. Solid lines here indicate communication channels.

### Description

Each [constellation] instance can for now be thought of as a single tab or window, and manages a pipeline of tasks that accepts input, runs JavaScript against the DOM, performs layout, builds display lists, renders display lists to tiles and finally composites the final image to a surface.

The pipeline consists of three main tasks:

* _[Script](#script)_—Script's primary mission is to create and own the DOM and execute the JavaScript engine. It receives events from multiple sources, including navigation events, and routes them as necessary. When the content task needs to query information about layout it must send a request to the layout task.
* _[Layout](#compositor)_—Layout takes a snapshot of the DOM, calculates styles, and constructs the two main layout data structures, the *[box tree](#box-tree)* and the *[fragment tree](#fragment-tree)*. The fragment tree is used to untransformed position of nodes and from there to build a display list, which is sent to the compositor.
* _[Compositor](#compositor)_—The compositor forwards display lists to [WebRender], which is the content rasterization and display engine used by both Servo and Firefox. It uses the GPU to render to the final image of the page. As the UI thread, the compositor is also the first receiver of UI events, which are generally immediately sent to content for processing (although some events, such as scroll events, can be handled initially by the compositor for responsiveness).

## Script

TODO: For now see https://github.com/servo/servo/blob/master/components/script/script_thread.rs

### SpiderMonkey

Current state of, and outlook on, Servo's integration of SpiderMonkey: [[https://github.com/gterzian/spidermonkey_servo](https://github.com/gterzian/spidermonkey_servo) ](https://github.com/servo/servo/wiki/Servo-and-SpiderMonkey-Report)

### DOM Bindings

### Script Thread

### Layout DOM

## Layout

Servo has two layout systems:

 - Layout (Layout 2020): This is a new layout system for Servo which doesn't yet have all the features of the legacy layout, but will have support for proper fragmentation. For more on the benefits of the new layout system, see [[Layout 2020|Layout-2020]]. The architecture described below refers to the new layout system. For more information about why we wrote a new layout engine see the [[Servo-Layout-Engines-Report]].
 - Legacy layout (Layout 2013): This is the original layout engine written for Servo. This layout engine is currently in maintenance mode.

Layout happens in three phases: box tree construction, fragment tree construction, and display list construction. Once a display list is generated, it is sent to [WebRender] for rendering. When possible during tree construction, layout will try to use parallelism with Rayon. Certain CSS feature prevent parallelism such as floats or counters. The same code is used for both parallel and serial layout.

### Box Tree

The *box tree* is tree that represents the nested formatting contexts as described in the [CSS specification][formatting-context]. There are various kinds of formatting contexts, such as block formatting contexts (for block flow), inline formatting contexts (for inline flow), table formatting contexts, and flex formatting contexts. Each formatting context has different rules for how boxes inside that context are laid out. Servo represents this tree of contexts using nested enums, which ensure that the content inside each context can only be the sort of content described in the specification.

The box tree is just the initial representation of the layout state and generally speaking the next phase is to run the layout algorithm on the box tree and produce a fragment tree. Fragments in CSS are the results of splitting elements in the box tree into multiple fragments due to things like line breaking, columns, and pagination. Additionally during this layout phase, Servo will position and size the resulting fragments relative to their containing blocks. The transformation generally takes place in a function called `layout(...)` on the different box tree data structures.

Layout of the *box tree* into the *fragment tree* is done in parallel, until a section of the tree with floats is encountered. In those sections, a sequential pass is done and parallel layout can commence again once the layout algorithm moves across the boundaries of the block formatting context that contains the floats, whether by descending into an independent formatting context or finishing the layout of the float container.

[formatting-context]: https://drafts.csswg.org/css-display/#formatting-context

### Fragment Tree

The product of the layout step is a *fragment tree*. In this tree, elements that were split into different pieces due to line breaking, columns, or pagination have a fragment for every piece. In addition, each fragment is positioned relatively to a fragment corresponding to its containing block. For positioned fragments, an extra placeholder fragment, `AbsoluteOrFixedPositioned`, is left in the original tree position. This placeholder is used to build the display list in the proper order according the CSS painting order.

### Display List Construction

Once layout has created a *fragment tree*, it can move on to the next phase of rendering which is to produce a display list for the tree. During this phase, the *fragment tree* is transformed into a [WebRender] display list which consists of display list items (rectangles, lines, images, text runs, shadows, etc). WebRender does not need a large variety of display list items to represent web content.

In addition to normal display list items, WebRender also uses a tree of *spatial nodes* to represent transformations, scrollable areas, and sticky content. This tree is essentially a description of how to apply post-layout transformations to display list items. When the page is scrolled, the offset on the root scrolling node can be adjusted without immediately doing a layout. Likewise, WebRender has the capability to apply transformations, including 3D transformations to web content with a type of spatial node called a *reference frame*.

Clipping whether from CSS clipping or from the clipping introduced by the CSS `overflow` property is handled by another tree of *clip nodes*. These nodes also have *spatial nodes* assigned to them so that clips stay in sync with the rest of web content. WebRender decides how best to apply a series of clips to each item.

Once the display list is constructed it is sent to the compositor which forwards it to WebRender. 

## Compositor

TODO: See https://github.com/servo/servo/blob/master/components/compositing/compositor.rs

## Implementation Strategy

Concurrency is the separation of tasks to provide interleaved execution. Parallelism is the simultaneous execution of multiple pieces of work in order to increase speed. Here are some ways that we take advantage of both:

* _Task-based architecture_. Major components in the system should be factored into actors with isolated heaps, with clear boundaries for failure and recovery. This will also encourage loose coupling throughout the system, enabling us to replace components for the purposes of experimentation and research.
* _Concurrent rendering_. Both rendering and compositing are separate threads, decoupled from layout in order to maintain responsiveness. The compositor thread manages its memory manually to avoid garbage collection pauses.
* _Tiled rendering_. We divide the screen into a grid of tiles and render each one in parallel. Tiling is needed for mobile performance regardless of its benefits for parallelism.
* _Layered rendering_. We divide the display list into subtrees whose contents can be retained on the GPU and render them in parallel.
* _Selector matching_. This is an embarrassingly parallel problem. Unlike Gecko, Servo does selector matching in a separate pass from flow tree construction so that it is more easily parallelized.
* _Parallel layout_. We build the flow tree using a parallel traversal of the DOM that respects the sequential dependencies generated by elements such as floats.
* _Text shaping_. A crucial part of inline layout, text shaping is fairly costly and has potential for parallelism across text runs. Not implemented.
* _Parsing_. We have written a new HTML parser in Rust, focused on both safety and compliance with the specification. We have not yet added speculation or parallelism to the parsing.
* _Image decoding_. Decoding multiple images in parallel is straightforward.
* _Decoding of other resources_. This is probably less important than image decoding, but anything that needs to be loaded by a page can be done in parallel, e.g. parsing entire style sheets or decoding videos.
* _GC JS concurrent with layout_ - Under most any design with concurrent JS and layout, JS is going to be waiting to query layout sometimes, perhaps often. This will be the most opportune time to run the GC.

For information on the design of WebXR see the [in-tree documentation](https://github.com/servo/servo/blob/main/docs/components/webxr.md).

## Challenges

* _Parallel-hostile libraries_. Some third-party libraries we need don't play well in multi-threaded environments. Fonts in particular have been difficult. Even if libraries are technically thread-safe, often thread safety is achieved through a library-wide mutex lock, harming our opportunities for parallelism.
* _Too many threads_. If we throw maximum parallelism and concurrency at everything, we will end up overwhelming the system with too many threads.

## JavaScript and DOM bindings

We are currently using SpiderMonkey, although pluggable engines is a long-term, low-priority goal. Each content task gets its own JavaScript runtime. DOM bindings use the native JavaScript engine API instead of XPCOM. Automatic generation of bindings from WebIDL is a priority.

## Multi-process architecture

Similar to Chromium and WebKit2, we intend to have a trusted application process and multiple, less trusted engine processes. The high-level API will in fact be IPC-based, likely with non-IPC implementations for testing and single-process use-cases, though it is expected most serious uses would use multiple processes. The engine processes will use the operating system sandboxing facilities to restrict access to system resources.

At this time we do not intend to go to the same extreme sandboxing ends as Chromium does, mostly because locking down a sandbox constitutes a large amount of development work (particularly on low-priority platforms like Windows XP and older Linux) and other aspects of the project are higher priority. Rust's type system also adds a significant layer of defense against memory safety vulnerabilities. This alone does not make a sandbox any less important to defend against unsafe code, bugs in the type system, and third-party/host libraries, but it does reduce the attack surface of Servo significantly relative to other browser engines. Additionally, we have performance-related concerns regarding some sandboxing techniques (for example, proxying all OpenGL calls to a separate process).

## I/O and resource management

Web pages depend on a wide variety of external resources, with many mechanisms of retrieval and decoding. These resources are cached at multiple levels—on disk, in memory, and/or in decoded form. In a parallel browser setting, these resources must be distributed among concurrent workers.

Traditionally, browsers have been single-threaded, performing I/O on the "main thread", where most computation also happens. This leads to latency problems. In Servo there is no "main thread" and the loading of all external resources is handled by a single [resource manager] task.

[resource manager]: https://github.com/servo/servo/blob/master/components/net/resource_thread.rs

Browsers have many caches, and Servo's task-based architecture means that it will probably have more than extant browser engines (e.g. we might have both a global task-based cache and a task-local cache that stores results from the global cache to save the round trip through the scheduler). Servo should have a unified caching story, with tunable caches that work well in low-memory environments.

## References

Important research and accumulated knowledge about browser implementation, parallel layout, etc:

* [How Browsers Work](http://ehsan.github.io/how-browsers-work/#1) - basic explanation of the common design of modern web browsers by long-time Gecko engineer Ehsan Akhgari
* [More how browsers work](http://taligarsiel.com/Projects/howbrowserswork1.htm) article that is dated, but has many more details
* [Webkit overview](http://www.webkit.org/coding/technical-articles.html)
* [Fast and parallel web page layout (2010)](http://www.eecs.berkeley.edu/~lmeyerov/projects/pbrowser/pubfiles/paper.pdf) - Leo Meyerovich's influential parallel selectors, layout, and fonts. It advocates seperating parallel selectors from parallel cascade to improve memory usage. See also the [2013 paper for automating layout](http://eecs.berkeley.edu/~lmeyerov/projects/pbrowser/pubfiles/synthesizer2012.pdf) and the [2009 paper that touches on speculative lexing/parsing](http://www.eecs.berkeley.edu/~lmeyerov/projects/pbrowser/hotpar09/paper.pdf).
* [Servo layout on mozilla wiki](https://wiki.mozilla.org/Servo/StyleUpdateOnDOMChange)
* [Robert O'Callahan's mega-presentation](http://robert.ocallahan.org/2012/04/korea.html) - Lots of information about browsers
* [ZOOMM paper](http://dl.acm.org/citation.cfm?id=2442543) - Qualcomm's network prefetching and combined selectors/cascade
* [Strings in Blink](https://docs.google.com/document/d/1kOCUlJdh2WJMJGDf-WoEQhmnjKLaOYRbiHz5TiGJl14/edit#heading=h.6w5vu5wppuew)
* [Incoherencies in Web Access Control Policies](http://research.microsoft.com/en-us/um/people/helenw/papers/incoherencyAndWebAnalyzer.pdf) - Analysis of the prevelance of document.domain, cross-origin iframes and other wierdness
* [A Case for Parallelizing Web Pages](http://www.cs.uiuc.edu/homes/kingst/Research_files/mai12.pdf) -- Sam King's server proxy for partitioning webpages. See also his [process-isolation work that reports parallelism benefits](http://www.cs.uiuc.edu/homes/kingst/Research_files/tang10_1.pdf).
* [High-Performance and Energy-Efficient Mobile Web Browsing on Big/Little Systems](https://webspace.utexas.edu/yz4422/hpca13.pdf) Save power by dynamically switching which core to use based on automatic workload heuristic
* [C3: An Experimental, Extensible, Reconfigurable Platform for HTML-based Applications](http://research.microsoft.com/apps/pubs/default.aspx?id=150010) Browser prototype written in C# at Microsoft Research that provided a concurrent (though not successfully parallelized) architecture
* [CSS Inline vertical alignment and line wrapping around floats](https://github.com/dbaron/inlines-and-floats) - dbaron imparts wisdom about floats
* [Quark](http://goto.ucsd.edu/quark/) - Formally verified browser kernel
* [HPar: A Practical Parallel Parser for HTML](http://www.cs.ucr.edu/~zhijia/papers/taco13.pdf)
* [Gecko HTML parser threading](https://developer.mozilla.org/en-US/docs/Mozilla/Gecko/HTML_parser_threading)

[meyerovich]: http://www.eecs.berkeley.edu/~lmeyerov/projects/pbrowser/pubfiles/paper.pdf
[constellation]: https://github.com/servo/servo/blob/master/components/constellation/lib.rs
[webrender]: https://github.com/servo/webrender
