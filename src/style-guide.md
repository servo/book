# Style guide

- Use sentence case for chapter and section headings, e.g. “Getting started” rather than “Getting Started”
- Use permalinks when linking to source code repos — press `Y` in GitHub to get a permanent URL

## Markdown source

- Use one sentence per line with no column limit, to make diffs and history easier to understand

To help split sentences onto separate lines, you can replace `([.!?]) ` → `$1\n`, but watch out for cases like “e.g.”.
Then to fix indentation of simple lists, you can replace `^([*-] .*\n([* -].*\n)*)([^\n* -])` → `$1  $3`, but this won’t work for nested or more complex lists.

- For consistency, indent nested lists with two spaces, and use `-` for unordered lists

## Error messages

- Where possible, always include a link to documentation, Zulip chat, or source code — this helps preserve the original context, and helps us check and update our advice over time

The remaining rules for error messages are designed to ensure that the text is as readable as possible, and that the reader can paste their error message into find-in-page with minimal false negatives, without the rules being too cumbersome to follow.

**Wrap the error message in `<pre><samp>`, with `<pre>` at the start of the line.**
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
<th>Error message
<th>Markdown
<tbody>
<tr>
<td><pre><samp>thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: "Could not run `PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=\"1\" PKG_CONFIG_ALLOW_SYSTEM_LIBS=\"1\" \"pkg-config\" \"--libs\" \"--cflags\" \"fontconfig\"`</samp></pre>
<td><pre style="white-space: pre-wrap; word-break: break-all;"><code class="language-html">&lt;pre>&lt;samp>thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: "Could not run `PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=\"1\" PKG_CONFIG_ALLOW_SYSTEM_LIBS=\"1\" \"pkg-config\" \"--libs\" \"--cflags\" \"fontconfig\"`&lt;/samp>&lt;/pre></code></pre>
<tr>
<td><pre><samp>error[E0765]: ...
 --> src/main.rs:2:14
  |
2 |       println!("```);
  |  ______________^
3 | | }
  | |__^</samp></pre>
<td><pre><code class="language-html">&lt;pre>&lt;samp>error[E0765]: ...
 --> src/main.rs:2:14
  |
2 |       println!("```);
  |  ______________^
3 | | }
  | |__^&lt;/samp>&lt;/pre></code></pre>
</table>
