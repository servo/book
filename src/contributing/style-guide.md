# Style Guide

The majority of our style recommendations are automatically enforced via our automated linters.
This document has guidelines that are less easy to lint for.

Lots of code in Servo was written before these recommendations were agreed upon.
We welcome pull requests to bring project code up to date with the modern guidelines.

## Rust

In general, all Rust code in Servo is automatically formatted via `rustfmt` when you run `./mach fmt`, which should align your code with the official [Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide/).
In addition, Rust code should use [Rust API naming conventions](https://rust-lang.github.io/api-guidelines/naming.html).
There are a few non-obvious points in the naming conventions guide such as:

- The `get_` prefix is generally not used for getters in Rust code.
  An exception to this rule is when it is used for a variant of a `get()` method like in `std::cell::Cell::get_mut()`.
- When camel-casing, acronyms and contractions of compound words count as one word.
  For instance, a struct should be called `HtmlParser` and not `HTMLParser`.

### Indentation

In order to make the flow of complicated functions and methods easier to follow, we try to minimize indentation by using early returns.
This also matches the language used in specifications in many cases.
When the logic of a function reaches 2 or 3 levels of indentation or when a short conditional block is an exceptional case that drops to the bottom of a long function, you should consider using an early return.
Early returns work very well when combined with the necessity to unwrap `Option`s or `enum` variants.
Prefer the following syntax when returning early when an `Option` value is `None`:

```rust
let Some(inner_value) = option_value else {
    return
};
```

This also works for `enum` variants as well:

```rust
enum Pet {
    Dog(usize),
    Cat(usize),
}

let pet = Pet::Dog(10);
let Pet::Dog(age) = pet else {
   return;
};
```

### Abbreviation

Servo follows the Google C++ guide [rules for naming](https://google.github.io/styleguide/cppguide.html#General_Naming_Rules).
Avoid abbreviations that would not be known to someone outside of the project.
Do not abbreviate by deleting letters in the middle of words.

**Exception:**:
You may use some universally-known abbreviations, such as the use of `i` for a loop index.
You may also use single letters such as `T` for Rust type parameters.

### Dead code

In almost all cases, do not commit dead code or commented out code to the repository.
Commented out code can [bit rot](https://en.wikipedia.org/wiki/Software_rot) easily and dead code is not tested.
When code becomes dead because it is completely unused, it should be removed.


**Exception:**
An exception for this case is when code is dead only one in some compilation configurations.
In that case, you use use an `expect(dead_code)` compiler directive with a configuration qualifier.
For example:

```rust
#[cfg_attr(any(target_os = "android", target_env = "ohos"), expect(dead_code))]
pub(crate) const LINE_HEIGHT: f32 = 76.0;
```

In this case, the `LINE_HEIGHT` constant is compiled, but expected to be dead when compiling for Android or OpenHarmony.

### `unsafe` code

Try to avoid unsafe code.
Unfortunately, a web engine is complicated so some amount of unsafe code is inevitable in Servo.
In the case that you have to make an `unsafe` function, use [Safety comments](https://std-dev-guide.rust-lang.org/policy/safety-comments.html#safety-comments), which explain why a block is safe and what the safety invariants are.
Use good judgement about when to add safety comments to `unsafe` blocks inside of functions.

### Assertions

When Servo's internal logic should make a certain condition impossible, use an `assert!` or `debug_assert!` statement to ensure that is the case.
You should think of `assert!` as both a kind of a test and a kind of documentation.
If the invariant expressed in the assertion ever becomes false, Servo might begin to crash when running tests, preventing the introduction or logic errors.
In addition, people reading the code can know what the author presumed to be true at a given point in the code in a stronger way than a comment allows.
If a particular part of a code is unreachable, for instance if an enum variant was handled before and shouldn't be encountered later in the same function, use `unreachable!()`, but always filling the text with why the code is unreachable.

### `unwrap()` and `expect()`

`unwrap` on `Option` or `Result` should almost never be used.
Instead, handle the `None` or `Err` case, doing any necessary error handling.
Servo should not crash, when possible.
If `None` or an `Err` is impossible due to the logic of Servo-internal code *that does not involve external input or crates*, then you can use `expect()` like you would use an assertion.
The text passed as an argument to `expect()` should express why the value cannot be `None` or `Err`.

**Exception:**:
When dealing with Rust's `std::sync::Mutex`or other concurrency primitives which use [poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html#poisoning), it is appropriate to use `unwrap`.

### `todo!()` and `unimplemented!()`

In code that is reachable via execution, do not use `todo!` or `unimplemented!`.
These macros will cause Servo to panic and normal web content shouldn't cause Servo to panic.
Intead, try to make these kind of cases unreachable and return proper error values or simply have the code do nothing instead.

## Shell scripts

Shell scripts are suitable for small tasks or wrappers, but it's preferable to use Python for anything with a hint of complexity or in general.

Shell scripts should be written using bash, starting with this shebang:
```
#!/usr/bin/env bash
```

Note that the version of bash available on macOS by default is quite old, so be careful when using new features.

Scripts should enable a few options at the top for robustness:
```
set -o errexit
set -o nounset
set -o pipefail
```

Remember to quote all variables, using the full form: `"${SOME_VARIABLE}"`.

Use `"$(some-command)"` instead of backticks for command substitution.
Note that these should be quoted as well.

## Servo Book

- Use permalinks when linking to source code repos — press `Y` in GitHub to get a permanent URL

### Markdown source

- Use one sentence per line with no column limit, to make diffs and history easier to understand

To help split sentences onto separate lines, you can replace `([.!?]) ` → `$1\n`, but watch out for cases like “e.g.”.
Then to fix indentation of simple lists, you can replace `^([*-] .*\n([* -].*\n)*)([^\n* -])` → `$1  $3`, but this won’t work for nested or more complex lists.

- For consistency, indent nested lists with two spaces, and use `-` for unordered lists

### Notation

- Use **bold text** when referring to UI elements like menu options, e.g. “click **Inspect**”
- Use `backticks` when referring to single-letter keyboard keys, e.g. “press `A` or Ctrl+`A`”

### Error messages

- Where possible, always include a link to documentation, Zulip chat, or source code — this helps preserve the original context, and helps us check and update our advice over time

The remaining rules for error messages are designed to ensure that the text is as readable as possible, and that the reader can paste their error message into find-in-page with minimal false negatives, without the rules being too cumbersome to follow.

**Wrap the error message in `<pre><samp>`, with `<pre>` at the start of the line (not indented).**
If you want to style the error message as a quote, wrap it in `<pre><blockquote><samp>`.

`<pre>` treats newlines as line breaks, and at the start of the line, it [prevents](https://spec.commonmark.org/0.31.2/#example-169) Markdown syntax from accidentally [taking effect when there are blank lines](https://spec.commonmark.org/0.31.2/#example-188) in the error message.

`<samp>` marks the text as computer output, where [we have CSS](../custom.css) that makes it wrap like it would in a terminal.
Code blocks (`<pre><code>`) don’t wrap, so they can make long errors hard to read.

**Replace every `&` with `&amp;`, then replace every `<` with `&lt;`.**
Text inside `<pre>` will never be treated as Markdown, but it’s still HTML markup, so it needs to be escaped.

**Always check the rendered output to ensure that all of the symbols were preserved.**
You may find that you still need to escape some Markdown with `\`, to avoid rendering <samp>called \`Result::unwrap()\` on an \`Err\` value</samp> as <samp>called `Result::unwrap()` on an `Err` value</samp>.

<table>
<thead>
  <tr>
    <th>Error message</th>
    <th>Markdown</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>
<pre><samp>thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: "Could not run `PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=\"1\" PKG_CONFIG_ALLOW_SYSTEM_LIBS=\"1\" \"pkg-config\" \"--libs\" \"--cflags\" \"fontconfig\"`</samp></pre>
    </td>
    <td>
      <pre style="white-space: pre-wrap; word-break: break-all;"><code class="language-html">&lt;pre>&lt;samp>thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: "Could not run `PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=\"1\" PKG_CONFIG_ALLOW_SYSTEM_LIBS=\"1\" \"pkg-config\" \"--libs\" \"--cflags\" \"fontconfig\"`&lt;/samp>&lt;/pre></code></pre>
    </td>
  </tr>
  <tr>
    <td>
<pre><samp>error[E0765]: ...
 --> src/main.rs:2:14
  |
2 |       println!("```);
  |  ______________^
3 | | }
  | |__^</samp></pre>
    </td>
    <td>
      <pre><code class="language-html">&lt;pre>&lt;samp>error[E0765]: ...
 --> src/main.rs:2:14
  |
2 |       println!("```);
  |  ______________^
3 | | }
  | |__^&lt;/samp>&lt;/pre></code></pre>
    </td>
  </tr>
</tbody>
</table>
