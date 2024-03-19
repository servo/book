<!-- TODO: needs copyediting -->

# mach

`mach` is a python utility that does plenty of things to make our life easier (build, run, run tests, update dependencies… see `./mach --help`).
Beside editing files and git commands, everything else is done via `mach`.

```shell
./mach run -d [mach options] -- [servo options]
```

The `--` separates `mach` options from `servo` options.
This is not required, but we recommend it.
`mach` and `servo` have some options with the same name (`--help`, `--debug`), so the `--` makes it clear where options apply.

## mach and Servo options

This guide only covers the most important options.
Be sure to look at all the available mach commands and the servo options:

```shell
./mach --help         # mach options
./mach run -- --help  # servo options
```
