The Servo Book
==============

**<https://book.servo.org>**

To render the book locally:

```sh
$ cargo install mdbook --vers '^0.4' --locked
$ cargo install mdbook-mermaid --vers '^0.13' --locked
$ mdbook serve --open
```

Or if you have [Nix](https://nixos.org/download/) (the package manager):

```sh
$ nix-shell --run 'mdbook serve --open'
```

**This book is still in early development!**
In the table of contents, \* denotes chapters that have been imported from our existing docs, and still need to be copyedited or reworked.
During this early stage of development, we’ll be frequently rewriting the Git history, so please be patient with us when making pull requests.
