# Building for OpenHarmony

<div class="warning _note">
Support for OpenHarmony is currently in-progress and these instructions might change from time to time and might also be incomplete.
</div>

## Get the OpenHarmony tools

Building for OpenHarmony requires the following:

1. The OpenHarmony SDK. This is sufficient to compile servo as a shared library for OpenHarmony.
2. The `hvigor` build tool to compile an application into an app bundle and sign it.

### Setting up the OpenHarmony SDK

The OpenHarmony SDK is required to compile applications for OpenHarmony.
The minimum version of SDK that Servo currently supports is v5.0.2 (API-14).

#### Downloading via DevEco Studio

[DevEco Studio] is an IDE for developing applications for HarmonyOS NEXT and OpenHarmony.
It supports Windows and MacOS.
You can manage installed OpenHarmony SDKs by clicking File->Settings and selecting "OpenHarmony SDK".
After setting a suitable installation path, you can select the components you want to install for each available API version.
DevEco Studio will automatically download and install the components for you.


#### Manual installation of the OpenHarmony SDK (e.g. on Linux)

<div class="warning _note">
    Before rushing and downloading the OH SDK from gitee as described here, please note that you will also need hvigor to compile applications.
    hvigor is currently recommended to be downloaded via the HarmonyOS NEXT commandline tools package, which also contains a copy of the OpenHarmony SDK.
</div>

1. Go to the [OpenHarmony release notes] and select the version you want to compile for.
2. Scroll down to the section "Acquiring Source Code from Mirrors" and click the download link for the version of "Public SDK package for the standard system" matching your host system.
3. Extract the archive to a suitable location.
4. Switch into the SDK folder with `cd <sdk_folder>/<your_operating_system>`.
5. Create a sub-folder with the same name as the API version (e.g 14 for SDK v5.0.2) and switch into it.
6. Unzip the zip files of the individual components into the folder created in the previous step. Preferably use the `unzip` command on the command-line, or manually ensure that the unzipped bundles are called e.g. `native` and not `native-linux-x64-5.x.y.z`.

The following snippet can be used as a reference for steps 4-6:
```commandline
cd ~/ohos-sdk/linux
for COMPONENT in "native toolchains ets js previewer" do
    echo "Extracting component ${COMPONENT}"
    unzip ${COMPONENT}-*.zip
    API_VERSION=$(cat ${COMPONENT}/oh-uni-package.json | jq -r '.apiVersion')
    mkdir -p ${API_VERSION}
    mv ${COMPONENT} "${API_VERSION}/"
done
```
On windows, it is recommended to use 7zip to unzip the archives, since the windows explorer unzip tool is extremely slow.

[DevEco Studio]: https://developer.huawei.com/consumer/cn/deveco-studio
[OpenHarmony release notes]: https://gitee.com/openharmony/docs/tree/master/en/release-notes/
[HarmonyOS NEXT commandline tools]: https://developer.huawei.com/consumer/cn/download/

#### Manual installation of the HarmonyOS NEXT commandline tools

The [HarmonyOS NEXT commandline tools] contain the OpenHarmony SDK and the following additional tools:

- `codelinter` (linter)
- `hstack` (crash dump stack analysis tool)
- `hvigor` / `hvigorw` (build tool)
- `ohpm` (package manager)

Currently, the commandline tools package is not publicly available and requires a chinese Huawei account to download.

#### Manual installation of hvigor without the commandline tools

<div class="warning _note">
This section is not fully tested and may change based on user feedback.
It's recommended to install the commandline-tools bundle. If you decide to install manually, you need to take
care to install the hvigor version matching the requirements of your project.
</div>

`hvigor` (not the wrapper `hvigorw`) is also available via `npm`.
1. Install the same nodejs version as the commandline-tools ship.
   For HarmonyOS NEXT Node 18 is shipped. Ensure that the `node` binary is in PATH.
2. Install Java using the recommended installation method for your OS.
   The build steps are known to work with OpenJDK v17, v21 and v23.
   On MacOS, if you install Homebrew's [OpenJDK formula], the following additional command may need to be run after the installation:
   ```
   # For the system Java wrappers to find this JDK, symlink it with
   sudo ln -sfn $HOMEBREW_PREFIX/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk
   ```
2. Edit your `.npmrc` to contain the following line:

    ```
    @ohos:registry=https://repo.harmonyos.com/npm/
    ```

3. Install hvigor and the hvigor-ohos-plugin. This will create a `node_modules` directory in the current directory.
   ```commandline
   npm install @ohos/hvigor
   npm install @ohos/hvigor-ohos-plugin
   ```
4. Now you should be able to run `hvigor.js` in your OpenHarmony project to build a hap bundle:
   ```
   /path/to/node_modules/@ohos/hvigor/bin/hvigor.js assembleHap
   ```
[OpenJDK formula]: https://formulae.brew.sh/formula/openjdk#default

### Configuring hdc on Linux

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

## Signing configuration

Most devices require that the HAP is digitally signed by the developer to be able to install it.
When using the `hvigor` tool, this can be accomplished by setting a static `signingConfigs` object in the `build-profile.json5` file or by dynamically creating the `signingConfigs` array on the application context object in the `hvigorfile.ts` script.

The `signingConfigs` property is an array of objects with the following structure:

```json
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
```

Here `<encrypted password>` is a hexadecimal string representation of the plaintext password after being encrypted.
The key and salt used to encrypt the passwords are generated by DevEco Studio IDE and are stored on-disk alongside the certificate files and keystore, usually under `<USER HOME>/.ohos/config/openharmony`.

You can use the IDE to generate the information needed for password encryption, the required application and profile certificate files, and the keystore itself.

1. Open Project Structure dialog from `File > Project Structure` menu.
2. Under the 'Signing Config' tab, enable the 'Automatically generate signature' checkbox.

**NOTE: The signature autogenerated above is intended only for development and testing. For production builds and distribution via an App Store, the relevant configuration needs to be obtained from the App Store provider.**

Once generated, it is necessary to point `mach` to the above "signing material" configuration using the `SERVO_OHOS_SIGNING_CONFIG` environment variable.
The value of the variable must be a file path to a valid `.json` file with the same structure as the `signingConfigs` property given above, but with `certPath`, `storeFile` and `profile` given as *paths relative to the json file*, instead of absolute paths.


## Building servoshell

Before building servo you will need to set some environment variables.
[direnv](https://direnv.net) is a convenient tool that can automatically set these variables based on an `.envrc` file, but you can also use any other method to set the required environment variables.

`.envrc`:
```commandline
    export OHOS_SDK_NATIVE=/path/to/openharmony-sdk/platform/api-version/native

    # Required if the HAP must be signed. See the signing configuration section above.
    export SERVO_OHOS_SIGNING_CONFIG=/path/to/signing-configs.json

    # Required only when building for HarmonyOS:
    export DEVECO_SDK_HOME=/path/to/command-line-tools/sdk # OR /path/to/DevEcoStudio/sdk OR on MacOS /Applications/DevEco-Studio.app/Contents/sdk

    # Required only when building for OpenHarmony:
    # Note: The openharmony sdk is under ${DEVECO_SDK_HOME}/default/openharmony
    # Presumably you would need to replicate this directory structure
    export OHOS_BASE_SDK_HOME=/path/to/openharmony-sdk/platform

    # If you have the command-line tools installed:
    export PATH="${PATH}:/path/to/command-line-tools/bin/"
    export NODE_HOME=/path/to/command-line-tools/tool/node

    # Alternatively, if you do NOT have the command-line tools installed:
    export HVIGOR_PATH=/path/to/parent/directory/containing/node_modules  # Not required if `hvigorw` is in $PATH
```

If you use `direnv` and an `.envrc` file, please remember to run `direnv allow .` after modifying the `.envrc` file.
Otherwise, the environment variables will not be loaded.

The following command can then be used to compile the servoshell application for a 64-bit ARM device or emulator:

```commandline
./mach build --ohos --release [--flavor=harmonyos]
```

In `mach build`, `mach install` and `mach package` commands, `--ohos` is an alias for `--target aarch64-unknown-linux-ohos`.
To build for an emulator running on an x86-64 host, use `--target x86_64-unknown-linux-ohos`.
The default `ohos` build / package / install targets OpenHarmony.
If you want to build for HarmonyOS you can add `--flavor=harmonyos`.
Please check the [Signing configuration](#signing-configuration) and add a configuration with `"name": "hos"` and `"type": "HarmonyOS""` and the respective signing certificates.


## Installing and running on-device

The following command can be used to install previously built servoshell application on a 64-bit ARM device or emulator:

```commandline
./mach install --ohos --release [--flavor=harmonyos]
```

## Further reading

[OpenHarmony Glossary](https://gitee.com/openharmony/docs/tree/master/en/glossary.md)
