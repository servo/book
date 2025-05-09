The Servo Book
==============

**<https://book.servo.org>**

To render the book locally:

```sh
$ cargo install mdbook --vers '^0.4' --locked
$ cargo install mdbook-mermaid --vers '^0.15' --locked
$ mdbook serve --open
```

Or if you have [Nix](https://nixos.org/download/) (the package manager):

```sh
$ nix-shell --run 'mdbook serve --open'
```

**This book is a work in progress!**
In the table of contents, \* denotes chapters that were recently added or imported from older docs, and still need to be copyedited or reworked.
