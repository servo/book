# Debugging on OpenHarmony

It's recommended to read the general advice from the [Debugging section](debugging.md) first.
This section will only cover the differences that need to be considered on OpenHarmony.

## Starting servoshell from the commandline

When debugging, it can often be useful to start servo from the commandline instead of clicking the app icon, since we can pass parameters from the commandline.

```shell
# Run this command to see which parameters can be passed to an ohos app
hdc shell aa start --help
# Start servo from the commandline
hdc shell aa start -a EntryAbility -b org.servo.servo
# --ps=<arg> <value> can be used to pass arguments with values to servoshell.
# The space between arg and value is mandatory when using `--ps`, meaning `--ps=--log-filter warn` is
# correct while `--ps=--log-filter=warn` is not.
# For pure flags without a value use `--psn <flag>`
hdc shell aa start -a EntryAbility -b org.servo.servo --ps=--log-filter "warn"
# Use `-U <url>` to let servo load a custom URL.
hdc shell aa start -a EntryAbility -b org.servo.servo -U https://servo.org
```

## Logging

On OpenHarmony devices log messages can be saved and accessed via the `hilog` service:

```shell
# See the hilog help for a full list of arguments supported by hilog
hdc shell hilog --help
# View all logs (very verbose, includes all other apps)
hdc shell hilog
# All servo and Spidermonkey related logs
hdc shell hilog --domain=0xE0C3,0xE0C4
# Only Rust code from servo
hdc shell hilog --domain=0xE0C3
# Only spidermonkey C++ code
hdc shell hilog --domain=0xE0C4
# Filter by domain and log level
hdc shell hilog --domain=0xE0C3 --level=ERROR
```

### Log level

Whether log statements are visible depends on multiple conditions:

1. The compile-time max log level of the `log` crate. See [log compile-time filters].
  Note: The `release_max_level_<level>` features of the log crate check if `debug_assertions = false` is set
  to determine the release filters should apply or not.
2. The runtime `log` global filter per module filters set in servoshell. Since environment variables aren't an
  option to customize the log level, `servoshell` has the `--log-filter` option on ohos targets, which allows
  customizing the log filter of the `log` crate.
  By default servoshell sets a log filter which hides log statements from many crates, so you likely will need to
  set a custom log-filter if you aren't seeing the logs from the crate you are debugging.
3. The `hilog` base log filter. `hdc shell hilog --base-level=<log_level>`. Can be combined with `--domain` and `--tag`
  options to customize **which logs are saved**.
4. The `hilog` log filter when displaying logs: `hdc shell hilog --level=<level>`

Most of the time option 2 and/or 4 should be used, since they allow quick changes with recompiling.

[log compile-time filters]: https://docs.rs/log/latest/log/#compile-time-filters

### Hilog domains

`hilog` allows setting a custom integer called "domain" (between 0 and 0xFFFF) when logging, which allows developers to easily filter logs using the domain.
For Rust code in servo logged via the `log` crate we set [`0xE0C3`] as the domain and for Spidermonkey C++ code we set [`0xE0C4`].
These values are somewhat arbitrarily chosen.

[`0xE0C3`]: https://github.com/servo/servo/blob/384d8f1ff895f070397b7a5a384428b1678416c5/ports/servoshell/egl/ohos.rs#L420
[`0xE0C4`]: <TODO - link pending SM PR being merged.>

### Hilog privacy feature

`hilog` has a privacy feature, which by default hides values in logs (e.g. from `%d` or `%s` substitutions).
Log statements from Rust are generally unaffected by this, since the string formatting is done on the Rust side.
If you encounter this issue when viewing C/C++ logs, you can temporarily turn off the privacy feature by running:

```shell
hdc shell hilog -p off
```

### Devtools and port forwards

You can enable the devtools and connect to them remotely with Firefox. It is easiest to do this with the command line via
`hdc shell aa start -a EntryAbility -b org.servo.servo --psn=--devtools=1234`
To connect to an instance of Servo you have to forward the port with
`hdc fport tcp:1234 tcp:1234`. You should see a message that the forward succeeded. Now you can
connect to the devtools using `localhost:1234`.
