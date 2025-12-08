# Minimal Reproducible Test Cases

In order to identify exactly what is going wrong on a page, it's very important to know how to create a minimal reproducible test case.
Even if you don't plan to fix the issue, providing the test case will make the issue much easier for others to fix and also preserve the failure even if the original site changes.
The process of making a test case is fairly systematic and can be done by even very new web platform developers.
A minimally reproducible test case is almost always the first step toward fixing an issue and they can often be easily converted into Web Platform Tests.

## Basic approach

The basic approach to creating a minimal reproducible test case is to gradually remove unecessary content from a page until only the problematic part of the page remains.
What this means is that the original layout issue, DOM error, or crash still happens even though the source code is much smaller.
It may be that the error doesn't look or function exactly the same when the test case is created, but it should still produce bad results when compared with other browsers, crash or produce an error.
An important step is to compare the results with more than one other browser engine to see if the problem is actually a specification issue.
It's recommended that you also run the test case in Chrome, Firefox, and a WebKit-based browser like Safari.

## Minimizing

In order to start creating a minimal reproducible test case, you first must have a copy of the page on your computer.
In Chrome, save the page with the issue using "Webpage, Complete."
This ensure that all of the images, CSS, and JavaScript files are also saved to your computer.
Next, load the saved HTML file in Chrome and Servo to ensure that the page still functions and that the bug still appears in Servo.
Now it's time to reduce!
There are a few techniques you can use to do this:

- Look for a part of the page that is not relevant to the issue, such as a header, footer, etc.
  Remove those from the loaded HTML file in the Web Inspector, such as by highlighting the elements and pressing the *Delete* key on your keyboard.
  Save the page again and ensure that the bug is still there by loading the newly saved page.
  Keep going!
- If the issue is a layout issue, try removing all JavaScript loaded in the page.
  If by removing the JavaScript the issue goes away, undo your change and try removing other JavaScript.
- Try removing references to external stylesheets.
  If removing the stylesheet also removes the bug, then inline the stylesheet and gradually remove unrelated rules.
  If necessary you can use a type of binary elimination of style rules.
- Replace loaded images with a simple image tag with a `width` and a `height`.
  Not loading an external resource makes the test case a lot easier to reason about.
- When you only a few elements left on the page, try removing `class`, `id`, or other unecessary attributes.

You should continue the reduction process until the test case is as small as possible.
Often, as you do this, the nature of the bug becomes apparent and you are already half of the way toward fixing it.

## Lithium

[Lithium](https://github.com/MozillaSecurity/lithium) is a tool to automate the process above.
It works particularly well with crashes and is resilient to non-deterministic bugs.
