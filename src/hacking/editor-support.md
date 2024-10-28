# Editor support

## Visual Studio Code

By default, rust-analyzer tries to run `cargo` without `mach`, which will cause problems!
For example, you might get errors in the rust-analyzer extension about build scripts:

> The style crate requires enabling one of its 'servo' or 'gecko' feature flags and, in the 'servo' case, one of 'servo-layout-2013' or 'servo-layout-2020'.

If you are on NixOS, you might get errors about `pkg-config` or `crown`:

> thread 'main' panicked at 'called \`Result::unwrap()\` on an \`Err\` value: "Could not run \`PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=\\"1\\" PKG_CONFIG_ALLOW_SYSTEM_LIBS=\\"1\\" \\"pkg-config\\" \\"--libs\\" \\"--cflags\\" \\"fontconfig\\"\`

> [ERROR rust_analyzer::main_loop] FetchWorkspaceError: rust-analyzer failed to load workspace: Failed to load the project at /path/to/servo/Cargo.toml: Failed to read Cargo metadata from Cargo.toml file /path/to/servo/Cargo.toml, Some(Version { major: 1, minor: 74, patch: 1 }): Failed to run \`cd "/path/to/servo" && "cargo" "metadata" "--format-version" "1" "--manifest-path" "/path/to/servo/Cargo.toml" "--filter-platform" "x86_64-unknown-linux-gnu"\`: \`cargo metadata\` exited with an error: error: could not execute process \`crown -vV\` (never executed)

`mach` passes different RUSTFLAGS to the Rust compiler than plain `cargo`, so if you try to build Servo with `cargo`, it will undo all the work done by `mach` (and vice versa).

Because of this, and because Servo can currently only be built with `mach`, you need to configure the rust-analyzer extension to use `mach` in `.vscode/settings.json`:

```
{
    "rust-analyzer.rustfmt.overrideCommand": [ "./mach", "fmt" ],

    "rust-analyzer.check.overrideCommand": [
        "./mach", "cargo-clippy", "--message-format=json" ],
    "rust-analyzer.cargo.buildScripts.overrideCommand": [
        "./mach", "cargo-clippy", "--message-format=json" ],
}
```

If having your editor open still causes unwanted rebuilds on the command line, then you can try configuring the extension to use an alternate target directory.
This will require more disk space.

```
{
    "rust-analyzer.checkOnSave.overrideCommand": [
        "./mach", "cargo-clippy", "--message-format=json", "--target-dir", "target/lsp" ],
    "rust-analyzer.cargo.buildScripts.overrideCommand": [
        "./mach", "cargo-clippy", "--message-format=json", "--target-dir", "target/lsp" ],
}
```

To enable [optional build settings](building-servo.md#optional-build-settings), append each mach option separately:

```
{
    "rust-analyzer.checkOnSave.overrideCommand": [
        "./mach", "check", "--message-format=json", "--target-dir", "target/lsp",
        "--debug-mozjs", "--use-crown" ],
    "rust-analyzer.cargo.buildScripts.overrideCommand": [
        "./mach", "check", "--message-format=json", "--target-dir", "target/lsp",
        "--debug-mozjs", "--use-crown" ],
}
```

### NixOS users

If you are on NixOS and using `--use-crown`, you should also set CARGO_BUILD_RUSTC in `.vscode/settings.json` as follows, where `/nix/store/.../crown` is the output of `nix-shell etc/shell.nix --run 'command -v crown'`.

```
{
    "rust-analyzer.server.extraEnv": {
        "CARGO_BUILD_RUSTC": "/nix/store/.../crown",
    },
}
```

These settings should be enough to not need to run `code .` from within a `nix-shell etc/shell.nix`, but it wouldn’t hurt to try that if you still have problems.

When enabling rust-analyzer’s proc macro support, you may start to see errors like

> proc macro \`MallocSizeOf\` not expanded: Cannot create expander for /path/to/servo/target/debug/deps/libfoo-0781e5a02b945749.so: unsupported ABI \`rustc 1.69.0-nightly (dc1d9d50f 2023-01-31)\` rust-analyzer(unresolved-proc-macro)

This means rust-analyzer is using the wrong proc macro server, and you will need to configure the correct one manually.
Use mach to query the current sysroot path, and copy the last line of output:

```
$ ./mach rustc --print sysroot
NOTE: Entering nix-shell etc/shell.nix
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
