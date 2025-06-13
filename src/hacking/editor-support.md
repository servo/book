# Editor support

## Visual Studio Code

By default, rust-analyzer tries to run `cargo` without `mach`, which will cause issues due
to the special configuration that Servo currently needs to build. It's recommend that you add
the following to your project specific settings in `.vscode/settings.json`:

```json
{
    "rust-analyzer.rustfmt.overrideCommand": [ "./mach", "fmt" ],
    "rust-analyzer.check.overrideCommand": [
        "./mach",
        "clippy",
        "--message-format=json",
        "--target-dir",
        "target/lsp",
        "--features",
        "tracing,tracing-perfetto"
    ],
    "rust-analyzer.cargo.buildScripts.overrideCommand": [
        "./mach",
        "clippy",
        "--message-format=json",
        "--target-dir",
        "target/lsp",
        "--features",
        "tracing,tracing-perfetto"    ],
}
```

Notes:

- In the above excerpt, the language server is building into its own target directory, `target/lsp`, in order to avoid unwanted rebuilds.
  If you would like to save disk space you can remove the `--target-dir` and `target/lsp` arguments and the default target directory will be used.
- To enable [optional build settings](building-servo.md#optional-build-settings), simply add them to the build argument list in your configuration file.
- **Windows*: If you are on Windows, you will need to use `./mach.bat` instead of just `./mach`.
  If you do not, you may receive an error saying that the command executed is not a valid Win32 application.

### Autocompletions for platform-specific code

If you're cross-compiling, autocompletions and other LSP features might not work. This is because rust-analyzer is targeting the host platform by default.  

To enable LSP features for Android-specific code, add the following bit to your `.vscode/settings.json`:

```json
  "rust-analyzer.cargo.target": "aarch64-linux-android"
```

## Zed

If you are using Zed, you must do something very similar to what is described for Visual Studio Code, but the Zed configuration file expects a slightly different syntax.
In your `./zed/settings.json` file you need something like this:

```json
{
  "lsp": {
    "rust-analyzer": {
      "initialization_options": {
        "checkOnSave": true,
        "check": {
          "overrideCommand": [
            "./mach",
            "clippy",
            "--message-format=json",
            "--target-dir",
            "target/lsp",
            "--feature",
            "tracing,tracing-perfetto"
          ]
        },
        "cargo": {
          "allTargets": false,
          "buildScripts": {
            "overrideCommand": [
              "./mach",
              "clippy",
              "--message-format=json",
              "--target-dir",
              "target/lsp",
              "--feature",
              "tracing,tracing-perfetto"
            ]
          }
        },
        "rustfmt": {
          "extraArgs": [
            "--config",
            "unstable_features=true",
            "--config",
            "binop_separator=Back",
            "--config",
            "imports_granularity=Module",
            "--config",
            "group_imports=StdExternalCrate"
          ]
        }
      }
    }
  }
}
```

### NixOS

If you are on NixOS, you might get errors about `pkg-config` or `crown`:

> thread 'main' panicked at 'called \`Result::unwrap()\` on an \`Err\` value: "Could not run \`PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=\\"1\\" PKG_CONFIG_ALLOW_SYSTEM_LIBS=\\"1\\" \\"pkg-config\\" \\"--libs\\" \\"--cflags\\" \\"fontconfig\\"\`

> [ERROR rust_analyzer::main_loop] FetchWorkspaceError: rust-analyzer failed to load workspace: Failed to load the project at /path/to/servo/Cargo.toml: Failed to read Cargo metadata from Cargo.toml file /path/to/servo/Cargo.toml, Some(Version { major: 1, minor: 74, patch: 1 }): Failed to run \`cd "/path/to/servo" && "cargo" "metadata" "--format-version" "1" "--manifest-path" "/path/to/servo/Cargo.toml" "--filter-platform" "x86_64-unknown-linux-gnu"\`: \`cargo metadata\` exited with an error: error: could not execute process \`crown -vV\` (never executed)

`mach` passes different RUSTFLAGS to the Rust compiler than plain `cargo`, so if you try to build Servo with `cargo`, it will undo all the work done by `mach` (and vice versa).
Because of this, and because Servo can currently only be built with `mach`, you need to configure the rust-analyzer extension to use `mach` in `.vscode/settings.json`:

#### Using `crown`

If you are using `--use-crown`, you should also set CARGO_BUILD_RUSTC in `.vscode/settings.json` as follows, where `/nix/store/.../crown` is the output of `nix-shell --run 'command -v crown'`.

```
{
    "rust-analyzer.server.extraEnv": {
        "CARGO_BUILD_RUSTC": "/nix/store/.../crown",
    },
}
```

These settings should be enough to not need to run `code .` from within a `nix-shell`, but it wouldn’t hurt to try that if you still have problems.

#### Problems with proc macros

When enabling rust-analyzer’s proc macro support, you may start to see errors like

> proc macro \`MallocSizeOf\` not expanded: Cannot create expander for /path/to/servo/target/debug/deps/libfoo-0781e5a02b945749.so: unsupported ABI \`rustc 1.69.0-nightly (dc1d9d50f 2023-01-31)\` rust-analyzer(unresolved-proc-macro)

This means rust-analyzer is using the wrong proc macro server, and you will need to configure the correct one manually.
Use mach to query the current sysroot path, and copy the last line of output:

```
$ ./mach rustc --print sysroot
NOTE: Entering nix-shell /path/to/servo/shell.nix
info: component 'llvm-tools' for target 'x86_64-unknown-linux-gnu' is up to date
/home/me/.rustup/toolchains/nightly-2023-02-01-x86_64-unknown-linux-gnu
```

Then configure either your sysroot path or proc macro server path in `.vscode/settings.json`:

```
{
    "rust-analyzer.procMacro.enable": true,
    "rust-analyzer.cargo.sysroot": "[paste what you copied]",
    "rust-analyzer.procMacro.server": "[paste what you copied]/libexec/rust-analyzer-proc-macro-srv",
}
```
