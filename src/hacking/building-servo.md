<!-- TODO: needs copyediting -->

# Building Servo

Building Servo is quite easy.
Install the prerequisites described in the [README](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/README.md) file, then type:

```shell
./mach build -d
```

There are three main build profiles, which you can build and use independently of one another:

- debug builds, which allow you to use a debugger (lldb)
- release builds, which are slower to build but more performant
- production builds, which are used for official releases only

| profile    | mach option            | optimised? | debug<br>info? | debug<br>assertions? | finds resources in<br>current working dir? |
| ---------- | ---------------------- | ---------- | -------------- | -------------------- | ------------------------------------------ |
| debug      | `-d`                   | no         | yes            | yes                  | yes                                        |
| release    | `-r`                   | yes        | no             | yes(!)               | yes                                        |
| production | `--profile production` | yes        | yes            | no                   | no                                         |

You can change these settings in a servobuild file (see [servobuild.example](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/servobuild.example)) or in the root [Cargo.toml](https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/Cargo.toml).
