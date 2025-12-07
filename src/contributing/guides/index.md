# Guides

This sections contains a few guides for  techniques to perform common tasks when working on Servo.

# Fixing web content bugs

There are two main classes of web compatibility issues that can be observed in Servo.
Visual bugs are often caused by missing features or bugs in Servo's CSS and layout support,
while interactivity problems and broken content is often caused by bugs or missing features
in Servo's DOM and JavaScript implementation.

- For help fixing a bug with our implementation of the DOM see [Diangnosing DOM Errors](diagnosing-dom-errors.md).
- For help narrowing down issues, whether in layout or in the DOM, see [Minimal Reproducible Test Cases](minimal-reproducible-test-cases.md).

# Adding new features

Feature additions are not a great task for a new contributor, because there is often a long series of changes necessary to fully implement a feature in a web engine.
To get started though, see [Implementing a DOM API](implementing-a-dom-api.md).
