# The Servo Book

**[API docs](https://doc.servo.org/servo/)**

***

[_Servo_](https://servo.org) is a web browser engine written in the Rust programming language, and currently developed on 64-bit Linux, 64-bit macOS, 64-bit Windows, and Android.

Work is still ongoing to make Servo consumable as a webview library.
Currently, the recommended way to run Servo as a browser is via [_servoshell_](https://servo.org/download/), our [winit](https://crates.io/crates/winit) and [egui](https://crates.io/crates/egui)-based demo browser.
If you’d like to embed Servo in your own application, consider using [tauri-runtime-verso](https://github.com/versotile-org/tauri-runtime-verso), a custom [Tauri](https://tauri.app/) runtime, or [servo-gtk](https://github.com/nacho/servo-gtk), a GTK4-based web browser widget.

![Screenshot of servoshell](images/servoshell.png)

This book will be your guide to building and running servoshell, hacking on and contributing to Servo, the architecture of Servo, and how to consume Servo and its libraries.

**This book is a work in progress!**
In the table of contents, \* denotes chapters that were recently added or imported from older docs, and still need to be copyedited or reworked.

Contributions are always welcome.
Click the pencil button in the top right of each page to propose changes, or go to [servo/book](https://github.com/servo/book) for more details.

## Need help?

Join the [Servo Zulip](https://servo.zulipchat.com) if you have any questions.
Everyone is welcome!
