# Guidelines for writing useful pull requests

In Servo, commits in pull requests are squashed and the pull request title and description are used to create the final commit message ([example](https://github.com/servo/servo/commit/9f4f598f44518d6883257f04f2ed11a8edd732c0)].
It's important that the information in both the title and description fully describes the change, as it makes the commit useful for those looking at the repository history and makes Servo a healthier project as a whole.

The title should succinctly describe what a change does. Some tips:

* Prefix the title with the lower-case name of the crate you are working on.
  For example, if the change modifies code in the "script" crate, prefix the title with "script: ".
  If a change affects multiple crates, identify which crate is the primary "source" of the change or just omit the prefix.
* Titles should be written as an imperative (a request or command) sentence with a verb.
  For instance "layout: Skip box tree construction when possible."
  Try to avoid generic verbs such as "fix", "correct", or "improve" and instead describe what the fix does.
  Code can be fixed multiple times, but the message should more uniquely identify the change.
* Prefixes should be lower-case and the rest of the title should only capitalize the first word and proper nouns (such as the name of data structures or specification concepts such as WebDriver).
  When in doubt follow what is written in the specification.
  Please do not use "Title Casing for Commit Messages."

The commit description should:

* Describe the original problem or situation (perhaps linking to any open bugs).
* Describe how the change fixes the problem, improves the code, or prepares for some followup change.
* Explain any caveats with the change, such as newly failing tests, performance degradation, or uncovered edge cases.
  Discuss how these can be addressed in the future.
* Be written in multiple sentence paragraphs of text with either consistent wrapping (80 characters or less) or no wrapping at all (as GitHub will do this automatically).
