# DevTools

[Firefox DevTools](https://firefox-source-docs.mozilla.org/devtools-user) are a set of web developer tools that can be used to examine, edit and debug a website's HTML, CSS and Javascript.
Servo has support for a subset of DevTools functionality, allowing for simple debugging.

## Connect to Servo

1. Run servoshell with the DevTools server enabled.
   Use the same port as before.

```sh
./mach run --devtools=6080
```

2. Open Firefox and go to `about:debugging`.
   If this is your first time using the DevTools integration, go to "Setup" and add `localhost:6080` as a [network location](https://firefox-source-docs.mozilla.org/devtools-user/about_colon_debugging/index.html#connecting-over-the-network).

3. Using Firefox, on `about:debugging`, click on "Connect" on the sidebar next to `localhost:6080`.

![Setting up the port in Firefox](../images/devtools-firefox-setup.png)

4. Accept the incoming connection by pressing `y` on the terminal that is running Servo.

![Accept the connection in the terminal](../images/devtools-accept-connection.png)

5. Back in Firefox, select a web view and click "Inspect".
   A new window should open with the page's inspector.

![Inspect a tab](../images/devtools-inspect-tab.png)

## Using the inspector

The inspector window is divided in various tabs with different workspaces.
At the moment, "Inspector" and "Console" are working.

In the "Inspector" tab there are three columns.
From left to right:

- **The HTML tree**: Shows the document nodes.
  Allows to see, add or modify attributes by double clicking on the tag name or attribute.
- **The style inspector**: Displays the associated CSS styling for one element.
  The entries here come from the element's style attribute, from a stylesheet or are inherited.
  Styles can be added or modified by clicking on the style name or the empty space below.
- **The extra column**: This contains more helpful tools.
  The two relevant ones are the "Layout" tab, which contains information about the box model properties of the element (flex and grid do not work yet), and "Computed", which contains a list of every calculated CSS value for the element.

![Inspector](../images/devtools-inspector.png)

The "Console" tab contains a functional JavaScript console that can interface with the website being displayed in Servo.
Errors, warnings and information that the website produces will be log here.
It can also be used to run JavaScript code directly on the website, for example, changing the document content or reloading the page:

```js
document.write("Hello, Servo!")
location.reload()
```

<div class="warning">

**Note:** Support for DevTools features is still a work in progress and it can break in future versions of Firefox if there are changes to the messaging protocol.
</div>
