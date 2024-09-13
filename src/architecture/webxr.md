# How WebXR works in Servo

## Terminology

Servo's WebXR implementation involves three main components:

1. The script thread (runs all JS for a page)
2. The WebGL thread (maintains WebGL canvas data and invokes GL operations corresponding to [WebGL APIs](https://registry.khronos.org/webgl/specs/latest/1.0/))
3. The compositor (AKA the main thread)

Additionally, there are a number of WebXR-specific concepts:

* The [discovery object](https://doc.servo.org/webxr_api/trait.DiscoveryAPI.html) (i.e. how Servo discovers if a device can provide a WebXR session)
* The [WebXR registry](https://doc.servo.org/webxr_api/struct.MainThreadRegistry.html) (the compositor's interface to WebXR)
* The [layer manager](https://doc.servo.org/webxr_api/layer/trait.LayerManagerAPI.html) (manages WebXR layers for a given session and frame operations on those layers)
* The [layer grand manager](https://doc.servo.org/webxr_api/layer/trait.LayerGrandManagerAPI.html) (manages all layer managers for WebXR sessions)

Finally, there are graphics-specific concepts that are important for the low-level details of rendering with WebXR:

* [Surfman](https://github.com/servo/webxr/blob/main/webxr/glwindow/mod.rs#L448-L452) is a crate that abstracts away platform-specific details of OpenGL hardware-accelerated rendering.
* A [surface](https://doc.servo.org/surfman/platform/unix/default/surface/type.Surface.html) is a hardware buffer that is tied to a specific OpenGL context.
* A [surface texture](https://doc.servo.org/surfman/platform/unix/default/surface/type.SurfaceTexture.html) is an OpenGL texture that wraps a surface.
  Surface textures can be shared between OpenGL contexts.
* A [surfman context](https://doc.servo.org/surfman/platform/unix/default/context/type.Context.html) represents a particular OpenGL context, and is backed by platform-specific implementations (such as EGL on Unix-based platforms).
* [ANGLE](https://github.com/servo/mozangle/) is an OpenGL implementation on top of Direct3D which is used in Servo to provide a consistent OpenGL backend on Windows-based platforms.

## How Servo's compositor starts

The embedder is responsible for creating a window and [triggering the rendering context creation](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/ports/servoshell/desktop/headed_window.rs#L134) appropriately.
Servo creates the rendering context by [creating a surfman context](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/shared/webrender/rendering_context.rs#L48-L58) which will be [used by the compositor](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/servo/lib.rs#L474) for all [web content rendering operations](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/servo/lib.rs#L266-L278).

## How a session starts

When a webpage invokes `navigator.xr.requestSession(..)` through JS, this corresponds to the [XrSystem::RequestSession](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/script/dom/xrsystem.rs#L158) method in Servo.
This method [sends a message](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr-api/registry.rs#L103-L108) to the [WebXR message handler](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr-api/registry.rs#L193-L195) that lives on the main thread, under the [control of the compositor](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/compositing/compositor.rs#L2416).

The WebXR message handler iterates over all known discovery objects and attempts to [request a session](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr-api/registry.rs#L217-L231) from each of them.
The discovery objects encapsulate creating a session for each supported backend.

As of July 19, 2024, there are three WebXR backends:

* [headless](https://github.com/servo/webxr/tree/main/webxr/headless) - supports a window-less, device-less device for automated tests
* [glwindow](https://github.com/servo/webxr/tree/main/webxr/glwindow) - supports a GL-based window for manual testing in desktop environments without real devices
* [openxr](https://github.com/servo/webxr/tree/main/webxr/openxr) - supports devices that implement the OpenXR standard

WebXR sessions need to [create a layer manager](https://github.com/servo/webxr/blob/main/webxr/glwindow/mod.rs#L448-L452)
at some point in order to be able to create and render to WebXR layers.
This happens in several steps:

1. Some initialization happens on the main thread
2. The main thread [sends a synchronous message](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/canvas/webgl_thread.rs#L3176-L3181) to the WebGL thread
3. The WebGL thread [receives the message](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/canvas/webgl_thread.rs#L390-L394)
4. Some backend-specific, graphics-specific initialization happens on the WebGL thread, hidden behind the [layer manager factory](https://doc.servo.org/webxr_api/struct.LayerManagerFactory.html) abstraction
5. The new layer manager is [stored in the WebGL thread](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/canvas/webgl_thread.rs#L3051-L3054)
6. The main thread [receives a unique identifier](https://github.com/servo/servo/blob/c6a6319502c3df4bf401d394a27854aa1f267658/components/canvas/webgl_thread.rs#L3183-L3191) representing the new layer manager

This cross-thread dance is important because the device performing the rendering often has strict requirements for the compatibility of any WebGL context that is used for rendering, and most GL state is only observable on the thread that created it.

## How an OpenXR session is created

The OpenXR discovery process starts at [OpenXrDiscovery::request_session](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/mod.rs#L311).
The discovery object only has access to whatever state was passed in its constructor, as well as a [SessionBuilder](https://doc.servo.org/webxr_api/struct.SessionBuilder.html) object that contains values required to create a new session.

Creating an OpenXR session first [creates an OpenXR instance](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/mod.rs#L227), which allows configuring which extensions are in use.
There are different extensions used to initialize OpenXR on different platforms; for Windows the [XR_KHR_D3D11_enable extension](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/graphics_d3d11.rs#L28) is used since Servo relies on ANGLE for its OpenGL implementation.

Once an OpenXR instance exists, the session builder is used to create a new WebXR session that [runs in its own thread](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/mod.rs#L339).
All WebXR sessions can either [run in a thread](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr-api/session.rs#L491-L516) or have Servo [run them on the main thread](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr-api/session.rs#L518-L531).
This choice has implications for how the graphics for the WebXR session can be set up, based on what GL state must be available for sharing.

OpenXR's new session thread [initializes an OpenXR device](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/mod.rs#L340-L344), which is responsible for creating the actual OpenXR session.
This session object is [created on the WebGL thread](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/mod.rs#L879-L909) as part of creating the OpenXR layer manager, since it relies on [sharing the underlying GPU device](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/graphics_d3d11.rs#L55-L77) that the WebGL thread uses.

Once the session object has been created, the main thread can [obtain a copy](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/mod.rs#L909) and resume initializing the [remaining properties](https://github.com/servo/webxr/blob/5587c9236bac0a8b7b87b3a95b22882400461b46/webxr/openxr/mod.rs#L913-L1064) of the new device.
