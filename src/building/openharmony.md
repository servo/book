# Building for OpenHarmony

<div class="warning _note">
Support for OpenHarmony is currently in-progress and these instructions might change from time to time and might also be incomplete.
</div>

## Prerequisites

OpenHarmony is an open-source operating system incubated and operated by the OpenAtom
Foundation. Servo can target it directly, or target HarmonyOS NEXT (Huawei's commercial
operating system based on OpenHarmony) by passing `--flavor=harmonyos` to `mach` (see below).

You will need:

- The **OpenHarmony SDK** — provides the sysroot and LLVM toolchain used to compile Servo.
  The minimum supported version is v6.0.0 (API-20).
- **cargo-ohos** — sets up the cross-compilation environment for `mach`. Install it with:

  ```shell
  ./mach bootstrap --ohos
  ```

- **hvigor** — required only to package the app into a `.hap` and sign it.

The next section covers the ways to obtain the SDK

## Getting the OpenHarmony SDK

### Preferred: DevEco Studio (macOS and Windows)

[DevEco Studio] is an IDE for developing applications for HarmonyOS NEXT and OpenHarmony.
It supports Windows and macOS and can download and manage OpenHarmony SDKs by clicking
File → Settings → OpenHarmony SDK.

- On **macOS**, Servo discovers the SDK automatically at
  `/Applications/DevEco-Studio.app/Contents/sdk`, so no extra configuration is needed.
- On **Windows**, point Servo at DevEco's SDK by setting an environment variable, for example:

  ```shell
  set DEVECO_SDK_HOME=%LOCALAPPDATA%\Huawei\Sdk
  ```

  (Alternatively, set `OHOS_SDK_NATIVE` to the SDK's `native` directory.)

### Manual: download with cargo-ohos

The simplest way that works on every platform — including Linux, where DevEco Studio is not
available — is to let cargo-ohos download the SDK:

```shell
cargo ohos init sdk --version=6.0.0.1
```

This downloads the SDK from the [openharmony-rs/ohos-sdk] mirror, verifies it,
and caches it. The command prints the environment variable to persist, 
for example:

```shell
export OHOS_SDK_NATIVE="$HOME/.cache/cargo-ohos/ohos-sdk/6.0.0.1/linux/20/native"
```

Add that line to your shell profile (e.g. `~/.bashrc`).

### Super-manual: download and extract by yourself

If neither DevEco Studio nor cargo-ohos is suitable, you can download the SDK yourself.

1. Go to the [OpenHarmony release notes] and select the version you want to compile for.
2. Scroll down to "Acquiring Source Code from Mirrors" and download the "Public SDK package
   for the standard system" matching your host system.
3. Extract the archive.
4. Unzip the individual components and group them under an API-version directory. The
   following snippet can be used as a reference:

   ```commandline
   cd ~/ohos-sdk/linux
   for COMPONENT in native toolchains ets js previewer; do
       unzip ${COMPONENT}-*.zip
       API_VERSION=$(jq -r '.apiVersion' < ${COMPONENT}/oh-uni-package.json)
       mkdir -p ${API_VERSION}
       mv ${COMPONENT} "${API_VERSION}/"
   done
   ```

   On Windows it is recommended to use 7zip to unzip the archives, since the Windows
   Explorer unzip tool is extremely slow.

5. Point Servo at the SDK:

   ```shell
   export OHOS_SDK_NATIVE=~/ohos-sdk/linux/<api-version>/native
   ```

## Packaging with hvigor

`hvigor` is needed only when packaging the app into a `.hap` bundle (with
`./mach package --ohos`) or installing it on a device. It is bundled with the
[HarmonyOS NEXT commandline tools], or can be installed via `npm`.

Currently, the commandline tools package is not publicly available and requires a Chinese
Huawei account to download.

<div class="warning _note">
The npm installation path below is not fully tested and may change based on user feedback.
Take care to install the hvigor version matching the requirements of your project.
</div>

1. Install a Node.js version supported by hvigor (Node 18 for HarmonyOS NEXT) and Java
   (OpenJDK v17, v21 or v23 are known to work).
2. Add the HarmonyOS npm registry to `.npmrc`:

   ```
   @ohos:registry=https://repo.harmonyos.com/npm/
   ```

3. Install hvigor and the plugin (this creates a `node_modules` directory):

   ```shell
   npm install @ohos/hvigor
   npm install @ohos/hvigor-ohos-plugin
   ```

`mach` finds hvigor either on `PATH` (as `hvigorw`) or via the `HVIGOR_PATH` environment
variable (the directory containing `node_modules`).

## Building servoshell

Once the SDK is available (see above), set the `OHOS_SDK_NATIVE` environment variable (unless
DevEco Studio is auto-discovered) and build:

```shell
export OHOS_SDK_NATIVE=/path/to/ohos-sdk/native
./mach build --ohos --release
```

For HarmonyOS NEXT, add `--flavor=harmonyos`. Please check the
[Signing configuration](#signing-configuration) and add a configuration with `"name": "hos"`
and `"type": "HarmonyOS"` and the respective signing certificates.

`--ohos` is an alias for `--target aarch64-unknown-linux-ohos`. To build for an emulator
running on an x86-64 host, use `--target x86_64-unknown-linux-ohos` instead. The default
build/package/install target is OpenHarmony.

A full `.envrc` (using [direnv](https://direnv.net)) might look like:

```commandline
export OHOS_SDK_NATIVE=/path/to/ohos-sdk/native

# Only needed to package/install a HAP (see "Packaging with hvigor" and "Signing configuration"):
export HVIGOR_PATH=/path/to/directory/containing/node_modules  # or have hvigorw on PATH
export SERVO_OHOS_SIGNING_CONFIG=/path/to/signing-configs.json
```

If you use `direnv` and an `.envrc` file, run `direnv allow .` after modifying it.

## Signing configuration

Most devices require that the HAP is digitally signed by the developer to be able to install it.
When using the `hvigor` tool, this can be accomplished by setting a static `signingConfigs` object in the `build-profile.json5` file or by dynamically creating the `signingConfigs` array on the application context object in the `hvigorfile.ts` script.

The `signingConfigs` property is an array of objects with the following structure:

```json
[
    {
        "name": "default",
        "type": "<OpenHarmony or HarmonyOS>",
        "material": {
            "certpath": "/path/to/app-signing-certificate.cer",
            "storePassword": "<encrypted password>",
            "keyAlias": "debugKey",
            "keyPassword": "<encrypted password>",
            "profile": "/path/to/signed-profile-certificate.p7b",
            "signAlg": "SHA256withECDSA",
            "storeFile": "/path/to/java-keystore-file.p12"
        }
    }
]
```

Here `<encrypted password>` is a hexadecimal string representation of the plaintext password after being encrypted.
The key and salt used to encrypt the passwords are generated by DevEco Studio IDE and are stored on-disk alongside the certificate files and keystore, usually under `<USER HOME>/.ohos`.

To generate the information needed for password encryption, the required application and profile certificate files, and the keystore itself, you can clone a [sample ArkTS app](https://github.com/jschwe/ServoDemo) and open it on DevEco Studio IDE.
Note that since signing information is tied to the bundle name, not all ArkTS app will work, and therefore it is **highly** recommended to use the sample ArkTS app mentioned above.

1. Open Project Structure dialog from `File > Project Structure` menu.
2. Under the 'Signing Config' tab, enable the 'Automatically generate signature' checkbox.

**NOTE: The signature autogenerated above is intended only for development and testing. For production builds and distribution via an App Store, the relevant configuration needs to be obtained from the App Store provider.**

>For Linux users, DevEco Studio is only available on Windows and MacOS. To proceed, **you will need another Windows / MacOS machine with DevEco Studio IDE installed** to create the signing keys. If you're developing for OpenHarmony boards (such as HopeRun development board), then you can name the `SigningConfigs` `default`. Otherwise, set it to `hos` if you're developing Servo for HarmonyOS devices (such as Huawei Mate series phones).
>
> Once the keys have been generated, you will need to move the entire directory that stores the keys (usually under `<USER HOME>/.ohos/`) generated by DevEco Studio from your Windows / MacOS machine.
>
> Additionally, you also need to copy `SigningConfigs` from `build-profile.json5` generated by DevEco Studio from your Windows / MacOS machine to a `.json` file in your Linux machine. This will serve as a "signing material" `mach` can later refer.

Once generated, it is necessary to point `mach` to the above "signing material" configuration using the `SERVO_OHOS_SIGNING_CONFIG` environment variable.
The value of the variable must be a file path to a valid `.json` file with the same structure as the `signingConfigs` property given above, but with `certPath`, `storeFile` and `profile` given as *paths relative to the json file*, instead of absolute paths.

## Configuring hdc on Linux

`hdc` is the equivalent to `adb` for OpenHarmony devices.
You can find it in the `toolchains` directory of your SDK.
For convenience purposes, you might want to add `toolchains` to your `PATH`.
Among others, `hdc` can be used to open a shell or transfer files between a device and the host system.
`hdc` needs to connect to a physical device via `usb`, which requires the user has permissions to access the device.

It's recommended to add a `udev` rule to allow hdc to access the corresponding device without needing to run `hdc` as root.
[This stackoverflow answer](https://stackoverflow.com/a/53887437) also applies to `hdc`.
Run `lsusb` and check the vendor id of your device, and then create the corresponding `udev` rule.
Please note that your user should be a member of the group you specify with `GROUP="xxx"`.
Depending on your Linux distributions you may want to use a different group.

To check if `hdc` is now working, you can run `hdc list targets` and it should show your device serial number.
If it doesn't work, try rebooting.

Please note that your device needs to be in "Developer mode" with USB debugging enabled.
The process here is exactly the same as one android:
1. Tap the build number multiple times to enable developer mode.
2. Then navigate to the developer options and enable USB debugging.
3. When you connect your device for the first time, confirm the pop-up asking you if you want to trust the computer you are connecting to.

## Installing and running on-device

The following command can be used to install previously built servoshell application on a 64-bit ARM device or emulator:

```commandline
./mach install --ohos --release [--flavor=harmonyos]
```

## Further reading

[OpenHarmony Glossary](https://gitee.com/openharmony/docs/tree/master/en/glossary.md)

## Troubleshooting

Be sure to look at the [General Troubleshooting](general-troubleshooting.md) section if you have trouble with your build.

[DevEco Studio]: https://developer.huawei.com/consumer/cn/deveco-studio
[openharmony-rs/ohos-sdk]: https://github.com/openharmony-rs/ohos-sdk
[OpenHarmony release notes]: https://gitee.com/openharmony/docs/tree/master/en/release-notes/
[HarmonyOS NEXT commandline tools]: https://developer.huawei.com/consumer/cn/download/
