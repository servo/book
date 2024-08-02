# Building for OpenHarmony 

<div class="warning _note">
Support for OpenHarmony is currently in-progress and these instructions might change from time to time and might also be incomplete.
</div>

## Get the OpenHarmony tools

Building for OpenHarmony requires the following: 

1. The OpenHarmony SDK. This is sufficient to compile servo as a shared library for OpenHarmony.
2. The `hvigorw` build tool to compile apps into an app bundle and sign it.

### Setting up the OpenHarmony SDK

The OpenHarmony SDK is required to compile applications for OpenHarmony. 

#### Downloading via DevEco Studio 

[DevEco Studio] is an IDE for developing applications for HarmonyOS NEXT and OpenHarmony.
It supports Windows and MacOS.
You can manage installed OpenHarmony SDKs by clicking File->Settings and selecting "OpenHarmony SDK".
After setting a suitable installation path, you can select the components you want to install for each available API version.
DevEco Studio will automatically download and install the components for you.


#### Manual installation of the OpenHarmony SDK (e.g. on Linux)

<div class="warning _note">
    Before rushing and downloading the OH SDK from gitee as described here, please note that you will also need `hvigor` to compile applications.
    `hvigor` is currently only available via the [HarmonyOS NEXT commandline tools], which also contains a copy of the OpenHarmony SDK.
</div>

Go to the [OpenHarmony release notes] and select the version you want to compile for.
Scroll down to the section "Acquiring Source Code from Mirrors" and click the download link for the version of "Public SDK package for the standard system" matching your host system.
Extract the archive to a suitable location.
Then switch into the SDK folder with `cd <sdk_folder>/<your_operating_system>` and unzip the zip files of the individual components.
Preferably use the `unzip` command on the command-line, or manually ensure that the unzipped bundles are called e.g. `native` and not `native-linux-x64-5.x.y.z`.
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
care to install the `hvigor` version matching the requirements of your project.
</div>

`hvigor` (not the wrapper `hvigorw`) is also available via `npm`. 
1. Install the same nodejs version as the commandline-tools ship.
   For HarmonyOS NEXT Node 18 is shipped.
2. Edit your `.npmrc` to contain the following line:

    ```
    @ohos:registry=https://repo.harmonyos.com/npm/
    ```

3. Install hvigor and the hvigor-ohos-plugin
   ```commandline
   npm install @ohos/hvigor
   npm install @ohos/hvigor-ohos-plugin
   ```
4. Set the following environment variables
    ```
    # Note: The openharmony sdk is under ${DEVECO_SDK_HOME}/HarmonyOS-NEXT-${HOS_VERSION}/openharmony
    # Presumably you would need to replicate this directory structure
    export DEVECO_SDK_HOME=/path/to/commandline-tools/sdk
    export NODE_HOME=/path/to/node
    export PATH=${NODE_HOME}/bin:$PATH
    ```
5. Now you should be able to run `hvigor.js` in your OpenHarmony project to build a hap bundle:
   ```
   /path/to/hvigor.js assembleHap
   ```

### Configuring hdc on Linux

`hdc` is the equivalent to `adb` for OpenHarmony devices. 
You can find it in the `toolchains` directory of your SDK.
For convenience purposes, you might want to add `toolchains` to your `PATH`.
Among others, `hdc` can be used to open a shell or send/receive files from a device
`hdc` needs to connect to a physical device via `usb`, which requires the user has permissions to access the device.

It's recommended to add a `udev` rule to allow hdc to access the corresponding device without needing to run `hdc` as root.
[This stackoverflow answer](https://stackoverflow.com/a/53887437) also applies to `hdc`.
Run `lsusb` and check the vendor id of your device, and then create the corresponding `udev` rule.
Please note that your user should be a member of the group you specify with `GROUP="xxx"`. 
Depending on your Linux distributions you may want to use a different group.

To check if `hdc` is now working, you can run `hdc list targets` and it should show your device serial number.
If it doesn't work, try rebooting.

Please note, that your phone needs to be in "Developer mode" with USB debugging enabled. 
The process here is exactly the same as one android:
1. Tap the build number multiple times to enable developer mode.
2. Then navigate to the developer options and enable USB debugging. 
3. When you connect your device for the first time, confirm the pop-up asking you if you want to trust the computer you are connecting to.

## Installing and running on-device

See the instructions in the repository for the Demo application: https://github.com/jschwe/ServoDemo

## Further reading

[OpenHarmony Glossary](https://gitee.com/openharmony/docs/tree/master/en/glossary.md)
