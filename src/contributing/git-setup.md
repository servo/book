# Git Setup

If you are new to Git or distrbuted version control, it's highly recommended that you spend some time learning the basics before continuing here.
There are many incredible resources online for learning Git.
For instance, the Zulip project maintains a [very thorough guide](https://zulip.readthedocs.io/en/latest/git/index.html) to using Git for contributing to an open source project.
The information there is often very relevant to working on Servo as well.
Becoming proficient with Git is a skill that will come in handy in many kinds of software development tasks and it's worth the time.

When you cloned Servo originally, the upstream Servo repository at `https://github.com/servo/servo` was your upstream.
You can choose to keep that configuration, but the recommneded workflow is the following:

1. [Fork](https://github.com/servo/servo/fork) the upstream Servo repository.
2. Check out a clone of your newly-forked copy of Servo.
   ```sh
   git clone --depth 10 https://github.com/<username>/servo.git
   ```
   Note that the `--depth 10` arguments here throw away most of Servo's commit history for better performance.
   They can be omitted.
3. Add a new remote named `upstream` that points at `servo/servo`.
   ```sh
   git remote add upstream https://github.com/servo/servo.git
   ```

## Starting a new change

When you want to work on a new change, you shouldn't do it on the `main` branch as that's where you want to keep your copy of the upstream repository.
Instead you should do your work on a branch.

1. Update your main branch to the latest upstream changes.
   ```sh
   git checkout main
   git pull origin main
   ```
2.  Create a new branch based on the main branch.
    ```sh
    git checkout -b issue-12345
    ```
3. Make your changes and commit them on that branch.
   Don't forget to [sign off on each commit](https://developercertificate.org/), too!
   ```sh
   git commit --signoff -m "script: Add a stub interface for MessagePort"
   ```

Next, you probably want to [make a pull request](making-a-pull-request.md) with your changes.
