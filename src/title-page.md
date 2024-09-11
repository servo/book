#伺服书

**[API文档](https://doc.servo.org/servo/)**

***

[_伺服系统_](https://servo.org)是用Rust编程语言编写的web浏览器引擎，目前在64位Linux、64位macOS、64位Windows和Android上开发。

使Servo作为webview库可消费的工作仍在进行中，所以现在，使用Servo唯一支持的方式是通过_伺服壳_，我们的[winit](https://crates.io/crates/winit)表示“对象”:　analysand[鄂桂](https://crates.io/crates/egui)基于的示例浏览器。

![Screenshot of servoshell](images/servoshell.png)

This book will be your guide to building and running servoshell, hacking on and contributing to Servo, the architecture of Servo, and how to consume Servo and its libraries.

**This book is a work in progress!**
In the table of contents, \* denotes chapters that were recently added or imported from older docs, and still need to be copyedited or reworked.

Contributions are always welcome.
Click the pencil button in the top right of each page to propose changes, or go to [servo/book](https://github.com/servo/book) for more details.

## Need help?

Join the [Servo Zulip](https://servo.zulipchat.com) if you have any questions.
Everyone is welcome!
