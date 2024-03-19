<!-- TODO: needs copyediting -->

# Architecture overview

Servo is a project to develop a new Web browser engine.
Our goal is to create an architecture that takes advantage of parallelism at many levels while eliminating common sources of bugs and security vulnerabilities associated with incorrect memory management and data races.

Because C++ is poorly suited to preventing these problems, Servo is written in [Rust](http://rust-lang.org), a new language designed specifically with Servo's requirements in mind.
Rust provides a task-parallel infrastructure and a strong type system that enforces memory safety and data race freedom.

When making design decisions we will prioritize the features of the modern web platform that are amenable to high-performance, dynamic, and media-rich applications, potentially at the cost of features that cannot be optimized.
We want to know what a fast and responsive web platform looks like, and to implement it.

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

This diagram shows the architecture of Servo in the case of only a single content process.
Servo is designed to support multiple content processes at once.
A single content process can have multiple script threads running at the same time with their own layout.
These have their own communication channels with the main process.
Solid lines here indicate communication channels.

### Description

Each [constellation] instance can for now be thought of as a single tab or window, and manages a pipeline of tasks that accepts input, runs JavaScript against the DOM, performs layout, builds display lists, renders display lists to tiles and finally composites the final image to a surface.

The pipeline consists of three main tasks:

* _[Script](#script)_—Script's primary mission is to create and own the DOM and execute the JavaScript engine.
  It receives events from multiple sources, including navigation events, and routes them as necessary.
  When the content task needs to query information about layout it must send a request to the layout task.
* _[Layout](#compositor)_—Layout takes a snapshot of the DOM, calculates styles, and constructs the two main layout data structures, the *[box tree](#box-tree)* and the *[fragment tree](#fragment-tree)*.
  The fragment tree is used to untransformed position of nodes and from there to build a display list, which is sent to the compositor.
* _[Compositor](#compositor)_—The compositor forwards display lists to [WebRender], which is the content rasterization and display engine used by both Servo and Firefox.
  It uses the GPU to render to the final image of the page.
  As the UI thread, the compositor is also the first receiver of UI events, which are generally immediately sent to content for processing (although some events, such as scroll events, can be handled initially by the compositor for responsiveness).
