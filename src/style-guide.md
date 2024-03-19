# Style guide

- Use sentence case for chapter and section headings, e.g. “Getting started” rather than “Getting Started”
- Use permalinks when linking to source code repos — press `Y` in GitHub to get a permanent URL

## Markdown source

- Use one sentence per line with no column limit, to make diffs and history easier to understand

To help split sentences onto separate lines, you can replace `([.!?]) ` → `$1\n`, but watch out for cases like “e.g.”.
Then to fix indentation of simple lists, you can replace `^([*-] .*\n([* -].*\n)*)([^\n* -])` → `$1  $3`, but this won’t work for nested or more complex lists.

- For consistency, indent nested lists with two spaces, and use `-` for unordered lists
