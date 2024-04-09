# Running servoshell

Once built, servoshell will be in `target/debug/servo` or `target/release/servo`.
You can [run it directly](../running-servoshell.md), but we recommend using [mach](mach.md) instead.

To run servoshell with mach, replace `./servo` with `./mach run -d --` or `./mach run -r --`, depending on the [build profile](building-servo.md) you want to run.
For example, both of the commands below run the debug build of servoshell with the same options:

```sh
$ target/debug/servo https://demo.servo.org
$ ./mach run -d -- https://demo.servo.org
```
