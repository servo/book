# Canvas

Servo supports four types of canvas context:

- [`CanvasRenderingContext2D`](https://github.com/servo/servo/blob/3babf7498656b9ff41b9d7894849a1921c68f28f/components/script/dom/canvasrenderingcontext2d.rs#L41) (`2d` context)
- [`WebGLRenderingContext`](https://github.com/servo/servo/blob/3babf7498656b9ff41b9d7894849a1921c68f28f/components/script/dom/webglrenderingcontext.rs#L173) (`webgl` context)
- [`WebGL2RenderingContext`](https://github.com/servo/servo/blob/3babf7498656b9ff41b9d7894849a1921c68f28f/components/script/dom/webgl2renderingcontext.rs#L95) (`webgl2` context)
- [`GPUCanvasContext`](https://github.com/servo/servo/blob/3babf7498656b9ff41b9d7894849a1921c68f28f/components/script/dom/webgpu/gpucanvascontext.rs#L65) (`webgpu` context)

Each canvas context implements [`CanvasContext` trait](https://github.com/servo/servo/blob/4f8d816385a5837844a3986cda392bb6c0464fe6/components/script/canvas_context.rs#L26), which requires contexts to implement some common features in a unified way:

- `context_id`
- `resize` this method clears painters image by setting it to transparent alpha (all bytes are zero)
- `get_image_data` used obtaining canvas image, usually by calling `toDataUrl`, `toBlob`, `createImageBitmap` on canvas or indirectly by drawing one canvas in another
- `update_the_rendering` for triggering update of image (usually by swapping screen-buffer and back-buffer)
- `canvas` to obtain connected canvas element (this can be `HTMLCanvasElement` or `OffscreenCanvas`, which can also be connected to `HTMLCanvasElement` with context set to `placeholder`)

while also providing some good default implementations (`onscreen`, `origin_is_clean`, `size`, `mark_as_dirty`). `mark_as_dirty` is called from functions that affect painters image and tells layout to rerender canvas element (by marking `HTMLCanvasElement` as dirty node).

## HTML event loop and rendering

```mermaid
flowchart TB
    subgraph Content Process
        subgraph Script flow
            JS-->utr[Update the rendering]-->layout
        end
    end

    subgraph Main Process
        subgraph painters
            WGPU[WGPU thread]
            WEBGL[WebGL thread]
            CPT[Canvas Paint Thread]
        end

        %% actual update in painters
        painters--CreateImage-->WR
        painters--UpdateImage-->WR

        WR[WebRender]
    end

    %% init canvas
    JS--create context-->painters--ImageKey-->JS

    %% update canvas rendering
    utr<--Update rendering-->painters

    %% rendering
    layout--DisplayList (contains ImageKey)-->WR
```

As part of HTML event loop, script thread first run some JS as part of [perform-a-microtask-checkpoint](https://html.spec.whatwg.org/multipage/#perform-a-microtask-checkpoint)
(this runs all microtasks from queue such as loading script, event, callbacks).
Next it [updates the rendering](https://html.spec.whatwg.org/multipage/webappapis.html#update-the-rendering), which for onscreen canvases requests generation of new images from the painter threads.
Then it performs a microtask checkpoint again, to [run the animation frame callbacks](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#run-the-animation-frame-callbacks).
Finally it triggers reflow (layout), which takes the DOM and its styles, builds a `DisplayList`, and sends that to WebRender for rendering.

```mermaid
sequenceDiagram
    loop Context Creation
        Script->>Painter: Crete Context
        Painter->>WebRender: CreateImage
        WebRender->>Painter: ImageKey
        Painter->>Script: ImageKey
    end

    loop Update The Rendering
        Script->>Painter:Update rendering
        Painter->>WebRender: UpdateImage
        opt
            Painter->>Script: Done
        end
    end

    loop Layout
        Script->>WebRender: DisplayList
        opt
            WebRender->>+Painter: lock ExternalImage
            WebRender->>Painter: unlock ExternalImage
            deactivate Painter
        end
    end
```

When canvas context creation is requested (`canvas.getContext('2d')`), the script thread blocks on the painter thread, which initializes and creates a new WebRender image (`CreateImage`), then sends the associated `ImageKey` back to script.
Each canvas context implements [`LayoutCanvasRenderingContextHelpers`](https://github.com/servo/servo/blob/4f8d816385a5837844a3986cda392bb6c0464fe6/components/script/canvas_context.rs#L17), which returns the `ImageKey` that layout will use in its `DisplayList`, or `None` if the canvas is cleared or otherwise not paintable due to its size.
WebRender will read the resultant image data when rendering, based on the provided `ImageKey`.
In WebGL and WebGPU painters, this is done by implementing a custom `WebrenderExternalImageApi` that provides `lock` and `unlock` methods for WebRender to obtain the actual image data, while for 2D canvases, image data is directly provided via `CreateImage` and `UpdateImage`.

## 2D canvas context

```mermaid
flowchart LR
    CanvasRenderingContext2d --- HTMLCanvasContext
    subgraph OffscreenCanvasRenderingContext2D
        subgraph CanvasRenderingContext2d
            CS'[CanvasState]
        end
    end
    OffscreenCanvasRenderingContext2D --- OffscreenCanvas
    PaintRenderingContext2D --- PaintWorklet
    subgraph PaintRenderingContext2D
        CS''[CanvasState]
    end
```

While most canvases use the same DOM type for their onscreen and offscreen contexts, this is not the case for 2D canvases due to their long history.
Web standards define three types of 2D canvas context:

- `CanvasRenderingContext2D` (connected to `HTMLCanvasContext`)
- `OffscreenCanvasRenderingContext2D` (connected to `OffscreenCanvas`)
- `PaintRenderingContext2D` (only available in `PaintWorklet`)

`CanvasRenderingContext2D` and `PaintRenderingContext2D` are implemented as wrappers around `CanvasState`, while `OffscreenCanvasRenderingContext2D` is implemented as a wrapper around `CanvasRenderingContext2D` because of similar logic to avoid duplication.

```mermaid
flowchart LR
    HTMLCanvasElement --getContext('2d')--> CanvasRenderingContext2d
    CanvasRenderingContext2d --strokeRect--> CanvasState
    CanvasState --IPC
    strokeRect--> CanvasPaintThread
    CanvasPaintThread --Done--> CanvasState
```

`CanvasState` implements the actual logic of 2D drawing, by setting appropriate state and sending IPC messages to the Canvas Paint Thread.
Some commands only change internal state, but don’t need to send any messages until there is an actual draw command.

[All "dirty" 2d canvases are stored in `Document`](https://github.com/servo/servo/blob/4974b4a1f638041ad99f4050256b168748e77ea9/components/script/dom/document.rs#L489) and are [flushed during reflow](https://github.com/servo/servo/blob/4974b4a1f638041ad99f4050256b168748e77ea9/components/script/dom/window.rs#L2196), by sending IPC messages that trigger the `update_the_rendering` method on each canvas.

When drawing one 2D canvas into another 2D canvas, we send `DrawImageInOther`, a special IPC message that avoids copying the bitmap out of the canvas paint thread.

## WebGL canvas context

```mermaid
flowchart LR
    WebGLRenderingContext --- c["HTMLCanvasElement
    OffscreenCanvas"]
    subgraph WebGL2RenderingContext
        WebGLRenderingContext
    end
```

WebGL(2) canvas context is `WebGLRenderingContext` (or `WebGL2RenderingContext` which wraps and extends `WebGLRenderingContext`), that contain methods that stores state and sends IPC messages to WebGL thread, which executes actual OpenGL(ES) commands and return results via IPC. This is done in blocking manner (we await for WebGL thread to complete operation).

All ["dirty" webgl canvases are stored in `Document`](https://github.com/servo/servo/blob/c915bf05fc9abcfba8a64cd4d50166a363a61109/components/script/dom/document.rs#L494) and are flushed on as part of reflow,
by [sending one IPC message containing all dirty context ids](https://github.com/servo/servo/blob/c915bf05fc9abcfba8a64cd4d50166a363a61109/components/script/dom/document.rs#L3333),
then blocking on WebGL thread until that is done.
Flushing swaps framebuffer, where one is for presentation (that is read by WebRender) while other is used for drawing (is target of execution of GL commands).

## WebGPU canvas context

WebGPU presentation is the most special as it is fully async (non-blocking).
More info about how async is done in WebGPU can be read in the [WebGPU chapter](./webgpu.md).

```mermaid
sequenceDiagram
    loop Context Creation
        Script->>WGPU: CreteContext
        WGPU->>WebRender: CreateImage
        WebRender->>WGPU: ImageKey
        WGPU->>Script: ImageKey
    end

    alt animation Callback
        Note over Script: getCurrentTexture
        Script-)WGPU:CreateTexture
        activate Script
        Note over Script: draw operations into current texture
    else update the rendering
    Note over Script: expire current texture
        Script-)WGPU:SwapchainPresent
        WGPU-)WGPU: Copy texture to one of staging buffer
        WGPU-)+WGPU poller: Map stagging buffer to CPU as GPUPresentationBuffer
        opt presentationId is newer than existing
            WGPU poller -)-WebRender: UpdateImage
        end
        WGPU poller -)WGPU poller: Unmap GPUPresentationBuffer

        Script-)WGPU:DestroyTexture
        deactivate Script

    end
    loop rendering
        WebRender<<->>+WGPU: lock ExternalImage and read GPUPresentationBuffer
        WebRender->>WGPU: unlock ExternalImage
        deactivate WGPU
    end
```

All onscreen WebGPU contexts have their [`update_the_rendering`](https://github.com/servo/servo/blob/c915bf05fc9abcfba8a64cd4d50166a363a61109/components/script/dom/webgpu/gpucanvascontext.rs#L261) executed as part of [updating the rendering](https://html.spec.whatwg.org/multipage/#update-the-rendering) in the HTML event loop.
This expires (destroys) the [current texture](https://developer.mozilla.org/en-US/docs/Web/API/GPUCanvasContext/getCurrentTexture), but before that we [send a SwapChainPresent request](https://github.com/servo/servo/blob/c915bf05fc9abcfba8a64cd4d50166a363a61109/components/script/dom/webgpu/gpucanvascontext.rs#L189), which copies texture data into one of 10 presentation buffers on the GPU.
After copying is done, we async map the new buffer to CPU.
Because this process is async, we mark each presentation buffer with an incrementing u64 id, and only replace the active presentation buffer if our buffer’s id is newer.
The inactive presentation buffer gets unmapped.

```mermaid
flowchart TD
    S[Staging Presentation Buffer] --copy_texture_to_buffer, mapAsync-->
    Mapping --mapAsync done-->
    UpdateWR --yes-->
    Mapped[Mapped, Unmapped old]

    UpdateWR--else unmap-->S
```

This is also modeled in TLA+: <https://gist.github.com/gterzian/aa5d96a89db280017b04917eee67f6ac>

Both WebRender's `lock` and `get_image_data` will use content of the [active presentation buffer](https://github.com/servo/servo/blob/c915bf05fc9abcfba8a64cd4d50166a363a61109/components/webgpu/swapchain.rs#L41).

## Resources

- <https://medium.com/@polyglot_factotum/fixing-servos-event-loop-490c0fd74f8d>
- <https://github.com/servo/servo/issues/35733>
- <https://github.com/servo/servo/pull/33521>
- <https://github.com/servo/servo/pull/34631>
- <https://github.com/servo/servo/pull/33613>
- <https://github.com/servo/servo/issues/33368>
