# Using git with Servo

Please follow this recommended workflow when making changes to Servo:

## Setup
Clone _your_ fork of Servo, and throw away most of Servo's commit history for better performance.
This is your `origin` remote.
Next, create a new remote named `upstream` that points at `servo/servo`.

```
git clone --depth 10 https://github.com/<username>/servo.git
git remote add upstream https://github.com/servo/servo.git
```

## Starting a new change

Update your main branch to the latest upstream changes. Next, create a new branch based on the main branch.

```
git checkout main
git pull origin main
git checkout -b issue-12345
```

## Committing changes

Use commit messages that summarize the changes that are included in each commit.
This helps Servo reviewers understand the context for those changes.
If the changes are mostly in one crate, it's helpful to prefix the commit message with the crate name.
Don't forget to [sign off on each commit](https://developercertificate.org/), too!

```
git commit --signoff -m "script: Add a stub interface for MessagePort."
```

The `-s` option can also be used in place of `--signoff`.

## Opening a pull request

First, push your branch to your `origin` remote.
Next, either open the URL that is returned by a successful push to start the pull request,
or visit your Servo fork in your web browser and follow the UI prompts.

```
jdm@pathfinder servo % git push origin issue-12345
Enumerating objects: 43, done.
Counting objects: 100% (43/43), done.
Delta compression using up to 12 threads
Compressing objects: 100% (29/29), done.
Writing objects: 100% (29/29), 5.13 KiB | 5.13 MiB/s, done.
Total 29 (delta 25), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (25/25), completed with 14 local objects.
remote:
remote: Create a pull request for 'issue-12345' on GitHub by visiting:
remote:      https://github.com/jdm/servo/pull/new/issue-12345
remote:
```

[!Screenshot of a GitHub UI button that says "Compare & pull request"](images/github-open-pr.png)

Please see the page on [writing a useful pull request](pr-description.md) for which details to include in your new pull request!

## Addressing review comments

Prefer appending new commits to your branch over amending existing commits.
This makes it easier for Servo reviewers to only look at the changes, which helps pull requests get reviewed more quickly.

```
git commit -s -m "script: Fix deadlock with cross-origin iframes."
git push origin issue-12345
```

## Addressing merge conflicts

When a pull request has merge conflicts, the two most common ways to address them are merging and rebasing.
Please do not press the "Update branch" button on the pull request; this performs a merge and will prevent some Servo CI functionality from working correctly.

[!Screenshot of a GitHub UI button that says "Update branch"](images/github-update-branch.png)

Instead, first update your local main branch, then rebase your feature branch on top of the main branch, then force push the changes.

```
git checkout issue-12345
git pull --rebase upstream main
git push -f origin issue-12345
```

When a rebase encounters conflicts, you will need to address them:

```
jdm@pathfinder servo % git rebase main issue-12345
Auto-merging components/script/dom/bindings/root.rs
CONFLICT (content): Merge conflict in components/script/dom/bindings/root.rs
Auto-merging components/script/dom/node.rs
error: could not apply 932c8d3e97d... script: Remove unused field from nodes.
hint: Resolve all conflicts manually, mark them as resolved with
hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
hint: You can instead skip this commit: run "git rebase --skip".
hint: To abort and get back to the state before "git rebase", run "git rebase --abort".
```

Please follow the GitHub documentation for [resolving conflicts](https://docs.github.com/en/get-started/using-git/resolving-merge-conflicts-after-a-git-rebase).
