# Android app architecture

The implementation of the Android app is divided into a number of components:
* the shared Android/OpenHarmony implementation of `servoshell` (`ports/servoshell/egl`)
* the Android-specific `servoshell` integration (`ports/servoshell/egl/android.rs`)
* the main Android activity (`support/android/apk/servoapp/src/main/java/org/servoshell`)
* the ServoView component (`support/android/apk/servoview/src/main/java/org/servo/servoview`)
  * the Android SurfaceView (`ServoView.java`)
  * the Servo library wrapper (`Servo.java`)
  * the JNI servoshell integration (`JNIServo.java`)

# Control flow

## Embedder -> Servo

Events that start inside the app are either initiated by the native app UI (eg. loading a URL) or as part of the Servo view (eg. a touch input).
All native app UI is defined in the main activity and uses the public API of the ServoView component to interact with the underlying Servo instance.

The ServoView is responsible for coordinating between two threads-the GL thread that's running the actual Servo instance, and the UI thread.
It is also responsible for forwarding input events to the engine and reacting to platform events like surface resizing.

## Servo -> Embedder

Events that start inside the engine need to reach various layers of the embedding app.
The lowest level is the Servo engine wrapper, which implements a `JNIServo.Callbacks` interface.
These callbacks allow the engine wrapper to trigger callbacks in the UI and GL threads according to the action that needs to occur.
Actions that take place in the UI thread include showing a prompt and triggering the onscreen keyboard, while GL thread actions include spinning the Servo event loop and performing GL rendering operations.
The Servo component exposes a `Client` interface for the UI thread actions, enabling communication with the highest layers of the embedding application.

# JNI integration

Every `native` member of the `JNIServo` class is implemented in the `android.rs` file as a `#[unsafe(no_mangle)]` function with a matching name.
The `jni-rs` crate [documentation](https://docs.rs/jni/latest/jni/) has more information on this ingration.
