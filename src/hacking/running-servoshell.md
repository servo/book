<!-- TODO: needs copyediting -->

# Running servoshell

The servo binary is located in `target/debug/servo` (or `target/release/servo`).
You can directly run this binary, but we recommend using `./mach` instead:

```shell
./mach run -d -- https://github.com
```

… is equivalent to:

```shell
./target/debug/servo https://github.com
```

If you build with `-d`, run with `-d`.
If you build with `-r`, run with `-r`.
