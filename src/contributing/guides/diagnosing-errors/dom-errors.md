# Diagnosing DOM Errors

Error message like the following clearly show that a certain DOM interface has not been implemented in Servo yet:
```
[2024-08-16T01:56:15Z ERROR script::dom::bindings::error] Error at https://github.githubassets.com/assets/vendors-node_modules_github_mini-throttle_dist_index_js-node_modules_smoothscroll-polyfill_di-75db2e-686488490524.js:1:9976 AbortSignal is not defined
```

However, error messages like the following do not provide much guidance:
```
[2024-08-16T01:58:25Z ERROR script::dom::bindings::error] Error at https://github.githubassets.com/assets/react-lib-7b7b5264f6c1.js:25:12596 e is undefined
```

Opening the JS file linked from the error message often shows a minified, obfuscated JS script that is almost impossible to read.
Let's start by unminifying it. Ensure that the `js-beautify` binary is in your path, or install it with:
```
npm install -g js-beautify
```

Now, run the problem page in Servo again with the built-in unminifying enabled:
```
./mach run https://github.com/servo/servo/activity --unminify-js
```

This creates an `unminified-js` directory in the root Servo repository and automatically persists unminified copies of each external JS script
that is fetched over the page's lifetime. Servo also evaluates the unminified versions of the scripts, so the line and column numbers in the
error messages also change:
```
[2024-08-16T02:05:34Z ERROR script::dom::bindings::error] Error at https://github.githubassets.com/assets/react-lib-7b7b5264f6c1.js:3377:66 e is undefined
```

You'll find `react-lib-7b7b5264f6c1.js` inside of `./unminified-js/github.githubassets.com/assets/`, and if you look at line 3377 you will
be able to start reading the surrounding code to (hopefully) determine what's going wrong in the page. If code inspection is not enough, however,
Servo also supports _modifying_ the locally-cached unminified JS!

```
./mach run https://github.com/servo/servo/activity --local-script-source unminified-js
```

When the `--local-script-source` argument is used, Servo will look for JS files in the provided directory first before attempting to fetch
them from the internet. This allows Servo developers to add `console.log(..)` statements and other useful debugging techniques to assist
in understanding what real webpages are observing. If you need to revert to a pristine version of the page source, just run with the
`--unminify-js` argument again to replace them with new unminified source files.
