# TODO: docs/STYLE_GUIDE.md

<!-- https://github.com/servo/servo/blob/b79e2a0b6575364de01b1f89021aba0ec3fcf399/docs/STYLE_GUIDE.md -->

# Style Guide

The majority of our style recommendations are automatically enforced via our automated linters.
This document has guidelines that are less easy to lint for.

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
