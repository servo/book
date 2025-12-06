# General Troubleshooting

<div hidden>

See the [style guide](../style-guide.md#error-messages) for how to format error messages.
</div>

If you run into trouble building Servo and you do not see your error listed on any other page, first try following the steps below:

1. **Ensure that you have all of the listed build requirements**.
   In particular, if you are using an uncommon Linux distribution or some other kind of Unix, you may need to determine what the correct name of a particular dependency is on your system.
2. **Double-check that build requirements are installed** and check [depenency versions](#dependency-versions).
3. **Run `./mach boostrap` or `.\mach boostrap` on Windows.**
   Sometimes the tools or dependencies needed to build Servo will change.
   It is safe to run this command more than once.
   Ensure that no errors were reported during execution.
   If you have installed other dependencies manually you may need to run `./mach bootstrap --skip-platform`.
4. **Refresh your environment**. This may involve:
   - Restarting your shell
   - Logging out and logging back in
   - Restarting your computer
   
## Dependency versions

- `curl --version` should print a version like 7.83.1 or 8.4.0
  - On Windows, type `curl.exe --version` instead, to avoid getting the PowerShell alias for `Invoke-WebRequest`
- `uv --version` should print **0.4.30 or newer**
  - Servo's `mach` build tool depends on `uv` to provision a pinned version of Python (set by the `.python-version` file in the repo) and create a local virtual environment (`.venv` directory) into which the python dependency modules are installed.
  - If the system already has an installation of the required Python version, then `uv` will just symlink to that installation to save disk space.
  - If the versions do not match or no Python installation is present on the host, then `uv` will download the required binaries.
  - Using an externally managed Python installation for executing `mach` as a Python script is currently not supported.
- `rustup --version` should print a version like 1.26.0
- **Windows**: `choco --version` should print a version like 2.2.2
- **macOS**: `brew --version` should print a version like 4.2.17

## You are not alone!

If you have problems building Servo that you can’t solve, you can always ask for help in the [build issues](https://servo.zulipchat.com/#narrow/stream/263398-general/topic/Build.20Issues) chat on Zulip.
