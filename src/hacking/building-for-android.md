<!-- TODO: needs copyediting -->

# Building for Android

### Support for Android is currently in-progress and these instructions might change frequently.

## Get Android tools

After cloning the repository and [installing dependencies common to all targets](https://github.com/servo/servo#setting-up-your-environment), you should obtain the Android SDK, either using the [Android Studio IDE](https://developer.android.com/studio) or via the `sdkmanager` CLI (which requires Java 17 or greater to be installed separately).

To install the NDK and SDK using Android Studio, refer to the guidelines on the website.
For the SDK, install the Android 33 platform.
The NDK must be version r26c.
Versions before and after change the layout of the NDK and add or remove files.

If you are using the `sdkmanager` tool, you can do:
```sh
sudo tools/bin/sdkmanager platform-tools "platforms;android-33" "build-tools;34.0.0" "ndk;26.2.11394342"
```

Set the following environment variables while building.
(You may want to export them from a configuration file like `.bashrc` (`~/.bash_profile` for Mac OS X).).
```sh
ANDROID_SDK_ROOT="/path/to/sdk"
ANDROID_NDK_ROOT="/path/to/ndk"
PATH=$PATH:$ANDROID_SDK/platform-tools
```

NOTE: If you are using Nix, you don't need to install the tools or setup the ANDROID_* environment variables manually.
Simply enable the Android build support running:
```
export SERVO_ANDROID_BUILD=1
```
in the shell session before invoking ./mach commands

## Build Servo

In the following sub-commands the `--android` flag is short for `--target aarch64-linux-android`

```sh
# Replace "--release" with "--dev" to create an unoptimized debug build.
./mach build --release --android
```

For running in an emulator however, you’ll likely want to build for Android x86-64 instead:

```sh
./mach build --release --target x86_64-linux-android
```

## Installing and running on-device

To install Servo on a hardware device, first [set up your device for development](https://developer.android.com/tools/device.html).

Run this command to install the Servo package on your device.
Replace `--release` with `--dev` if you are building in debug mode.

```
./mach install --release --android
```

To start Servo, tap the "Servo" icon in your launcher screen, or run this :

```
./mach run --android https://www.servo.org/
```

Force-stop:
```
adb shell am force-stop org.servo.servoshell/org.servo.servoshell.MainActivity
```
If the above doesn't work, try this:
```
adb shell am force-stop org.servo.servoshell
```

Uninstall:
```
adb uninstall org.servo.servoshell
```
### NOTE: The following instructions are outdated and might not apply any longer. They are retained here for reference until the Android build is fully functional and the below instructions are reviewed.

## Profiling

We are currently using a Nexus 9 for profiling, because it has an NVidia chipset and supports the NVidia System Profiler.
First, install the [profiler](https://developer.nvidia.com/tegra-system-profiler).

You will then need to root your Nexus 9.
There are a variety of options, but I found the [CF-Auto-Root](http://forum.xda-developers.com/showthread.php?t=1980683) version the easiest.
Just follow the instructions on that page (download, do the OEM unlock, `adb reboot bootloader`, `fastboot boot image/CF-Auto-Root-flounder-volantis-nexus9.img`) and you should end up with a rooted device.

If you want reasonable stack backtraces, you should add the flags `-fno-omit-frame-pointer -marm -funwind-tables` to the `CFLAGS` (simplest place to do so is in the mach python scripts that set up the env for Android).
Also, remember to build with `-r` for release!

## Installing and running in the emulator

To set up the emulator, use the `avdmanager` tool installed with the SDK.
Create a default Pixel 4 device with an SDCard of size greater than 100MB.
After creating it, open the file ~/.android/avd/nexus7.avd/config.ini and change the `hw.dPad` and `hw.mainKeys` configuration files to `yes`.

Installation:
```
./mach install --android --release
```

Running:
```
./mach run --android https://www.mozilla.org/
```

Force-stop:
```
adb shell am force-stop org.servo.servoshell
```

Uninstall:
```
adb uninstall org.servo.servoshell
```

## Viewing logs and stdout

By default, only libsimpleservo logs are sent to `adb logcat`.
`println` output is also sent to logcat (see [#21637](https://github.com/servo/servo/issues/21637)).
Log macros (`warn!`, `debug!`, …) are sent to logcat under the tag `simpleservo`.

To show all the servo logs, remove the log filters in [jniapi.rs](https://github.com/servo/servo/blob/1e1eca07edac2b842751e7182cc641a84bef52bc/ports/libsimpleservo/src/jniapi.rs#L62).

## Getting meaningful symbols out of crash reports


Copy the logcat output that includes the crash information and unresolved symbols to a temporary `log` file.
Run `ndk-stack -sym target/armv7-linux-androideabi/debug/apk/obj/local/armeabi-v7a/lib/ -dump log`.
This should resolve any symbols from libsimpleservo.so that appear in the output.
The `ndk-stack` tool is found in the NDK root directory.

## Debugging on-device

First, you will need to enable debugging in the project files by adding `android:debuggable="true"` to the `application` tag in servo/support/android/apk/app/src/main/AndroidManifest.xml.

```
~/android-ndk-r9c/ndk-gdb \
    --adb=/Users/larsberg/android-sdk-macosx/platform-tools/adb \
    --project=servo/support/android/apk/app/src/main/
    --launch=org.servo.servoshell.MainActivity \
    --verbose
```

To get symbols resolved, you may need to provide additional library paths (at the gdb prompt):  
`set solib-search-path /Users/larsberg/servo/support/android/apk/obj/local/armeabi/:/Users/larsberg/servo/support/android/apk/libs/armeabi`

OR you may need to enter the same path names as above in the support/android/apk/libs/armeabi/gdb.setup file.

If you are not able to get past the "Application Servo (process org.servo.servoshell) is waiting for the debugger to attach." prompt after entering `continue` at `(gdb)` prompt, you might have to set Servo as the debug app (Use the "Select debug app" option under "Developer Options" in the Settings app).
If this doesn't work, Stack Overflow will help you.

The ndk-gdb debugger may complain about `... function not defined` when you try to set breakpoints.
Just answer `y` when it asks you to set breakpoints on future library loads.
You will be able to catch your breakpoints during execution.

## x86 build

To build a x86 version, follow the above instructions, but replace `--android` with `--target=i686-linux-android`.
The x86 emulator will need to support GLES v3 (use AVS from Android Studio v3+).

## WebVR support

- Enable WebVR preference: "dom.webvr.enabled": true
- ./mach build --release --android --features googlevr
- ./mach package --release --android --flavor googlevr
- ./mach install --release --android
- ./mach run --android https://threejs.org/examples/webvr_rollercoaster.html (warning: the first run loads the default url sometimes after a clean APK install)

## PandaBoard

If you are using a PandaBoard, Servo is known to run on Android with the instructions above using the following build of Android for PandaBoard:
http://releases.linaro.org/12.10/android/leb-panda


## Important Notices.

Different from Linux or Mac, on Android, Servo's program entry is in the library, not executable.
So we can't execute the program with command line arguments.
To approximate command line arguments, we have a hack for program entry on android: You can put command-line arguments, one per line, in the file `/sdcard/servo/android_params` on your device.
You can find a default `android_params` property under `resources` in the Servo repo.

Default settings:
```sh
default font directory : /system/fonts (in android)
default resource path : /sdcard/servo (in android)
default font configuration : /sdcard/servo/.fcconfig (in android)
default fallback font : Roboto
```

## Working on the user interface without building Servo

We provide nightly builds of a servo library for android, so it's not necessary to do a full build to work on the user interface.

- Download the latest AAR: https://download.servo.org/nightly/android/servo-latest.aar (this is an armv7 build)
- In your local copy of Servo, create a file `support/android/apk/user.properties` and specify the path to the AAR you just downloaded: `servoViewLocal=/tmp/servo-latest.aar`
- open `support/android/apk` with Android Studio
- *important*: in the project list, you should see 2 projects: `servoapp` and `servoview-local`.
  If you see `servoapp` and `servoview` that means Android Studio didn't correctly read the settings.
  Re-sync gradle or restart Android Studio
- select the build variant `mainArmv7Debug` or `mainArmv7Release`
- plug your phone
- press the Play button

Alternatively, you can generate the APK with the command line:

```sh
wget https://download.servo.org/nightly/android/servo-latest.aar -O /tmp/servo-latest.aar
cd SERVO_REPO/support/android/apk
echo 'servoViewLocal=/tmp/servo-latest.aar' > user.properties
./gradlew clean
./gradlew :servoapp:assembleMainArmv7Release
cd ../../..
adb install -r target/armv7-linux-androideabi/release/servoapp.apk
```

The relevant files to tweak the UI are: MainActivity.java and activity_main.xml
