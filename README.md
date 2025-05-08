The Servo Book
==============

**<https://book.servo.org>**

**Getting the source**
Source files of the book [git repository](https://github.com/servo/book)
```bash
git clone https://github.com/servo/book.git
```

**Prerequisites**
First you must setup all necessary components to building local version of servobook. You will need the following cargo crates:
- mdbook
- mdbook-mermaid

We suggest to not compile this cargo crates from sources but rather install precompiled releases with [cargo-binstall](https://github.com/cargo-bins/cargo-binstall);
```bash
cargo binstall mdbook mdbook-mermaid
```

**Live modification**
Easiest way to work with documentation is to use:

```sh
$ mdbook serve --open
```

Or if you have [Nix](https://nixos.org/download/) (the package manager):

```sh
$ nix-shell --run 'mdbook serve --open'
```

It will serve a book at http://localhost:3000, and rebuild it on changes.
For full list of available comands use

```sh
mdbook --help
```

**Mermaid update**
Servo book uses [Mermaid Diagramming and charting tool](https://mermaid.js.org/).
You can find the example of such diagram in section [Architecture overview](architecture/overview.md). Sometimes you will want to use the newest syntax, and that tool is not automatically updated, so you may use the following steps to update the version within the project:
```bash
mdbook-mermaid install .
rm mermaid-init.js
mv mermaid.min.js src/mermaid.min.js
```

**This book is a work in progress!**
In the table of contents, \* denotes chapters that were recently added or imported from older docs, and still need to be copyedited or reworked.

**QA**
If you have any question you may find answers [on Zulip](https://servo.zulipchat.com).
@**Delan Azabani** is the original author of the book.
Please be patient and polite!
