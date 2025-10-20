# Building for Android

## Building

- Ensure that the following environment variables are set:
  - `ANDROID_SDK_ROOT`
  - `ANDROID_NDK_ROOT`: `$ANDROID_SDK_ROOT/ndk/28.2.13676358/`
 `ANDROID_SDK_ROOT` can be any directory (such as `~/android-sdk`).
  All of the Android build dependencies will be installed there.
- Install the latest version of the [Android command-line tools](https://developer.android.com/studio#command-tools) to `$ANDROID_SDK_ROOT/cmdline-tools/latest`.
- Run the following command to install the necessary components:
  ```shell
  sudo $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --install \
   "build-tools;34.0.0" \
   "emulator" \
   "ndk;28.2.13676358" \
   "platform-tools" \
   "platforms;android-33" \
   "system-images;android-33;google_apis;arm64-v8a"
  ```
- Run `./mach build --android -r`

**Note**: This will install dependencies and build Servo for the `aarch64-linux-android` platform.
In order to build Servo for other Android targets, ensure that you install the appropriate system images via `sdkmanager` and pass `--target` with a Rust compatible target to `mach` when building instead of `--android`.

**Note**: It's also possible to use an installation from [Android Studio](https://developer.android.com/studio).
Just ensure that the `ANDROID_SDK_ROOT` and `ANDROID_NDK_ROOT` variables are set properly.

**Note**: If you are not using Android Studio on macOS, you will need to install a JDK.
Use `brew install opendjdk@21` to install a usable version; newer versions cause `java.lang.IllegalArgumentException: 25` when running the gradle build step during the Servo build.

**Note**: If you are using Nix, you don't need to install the tools or set up the ANDROID_* environment variables manually.
Simply enable the Android build support running:

```
export SERVO_ANDROID_BUILD=1
```

in the shell session before invoking ./mach commands

## Running in the emulator

1. Create a new AVD image to run Servo:
    ```
    $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/avdmanager avdmanager create avd 
        --name "Servo" \
        --device "pixel" \
        --package "system-images;android-33;google_apis;arm64-v8a" \
        --tag "google_apis" \
        --abi "arm64-v8a
    ```
2. Enable the hardware keyboard.
   Open `~/.android/avd/Servo.avd/config.ini` and change `hw.keyboard = no` to `hw.keyboard = yes`.
3. Launch the emulator
   ```
   $ANDROID_SDK_ROOT/emulator/emulator -avd servo -netdelay none -no-snapshot
   ```
5. Install Servo on the emulator:
   ```
    ./mach install -r
   ```
6. Start Servo by tapping the Servo icon on your launcher screen.

## Installing on a physical device

1. [Set up your device for development](https://developer.android.com/studio/run/device).
2. Build Servo as described above, ensuring that you are building for the appropriate target for your device.
3. Install Servo to your device by running:
   ```
   ./mach install --release --android
   ```
4. Start Servo by tapping the Servo icon on your launcher screen or run:
   ```
   ./mach run --android https://www.servo.org/
   ```

You can request a force-stop of Servo by running:
```
adb shell am force-stop org.servo.servoshell/org.servo.servoshell.MainActivity
```

If the above doesn't work, try this:
```
adb shell am force-stop org.servo.servoshell
```

You can uninstall Servo by running:
```
adb uninstall org.servo.servoshell
```
