## Releasing a new servo version

### Bumping the servo version on main

Currently we release a new servo version every month.
At the end of the month, prepare a branch based on latest `main`.
Run `./mach release X.Y.Z` to bump the version numbers and commit the changes. 
Open a pull request on servo, to merge the branch into `main`.
Ideally, the pull request is merged timely on the last or the first day of the month, so that the version number bump correlates closely with the blog-post range.
The blog-post range is up to (including) the head of the last nightly release of the month.
The version bump should be merged **after** this commit, so that all changes mentioned in the blog post are included in the release.

### Creating a release branch

Create a branch with the name `release/vX.Y.Z`, based on the commit that bumped the version number (in `main`).
If the date of merge was (significantly) later, and significant changes were made, then the release branch can also be based on an earlier commit and the version number bump backported / re-applied.
The branch should be pushed to the upstream servo repository. 

### Creating a draft release for testing

Go to the `actions` tab of the servo repository, and select the [`Release` workflow](https://github.com/servo/servo/actions/workflows/release.yml).
Select the `Run workflow` button on the top right corner.
Choose the branch `release/vX.Y.Z` (that you just pushed) as the branch to run the workflow on.
Leave the tickbox **unchecked** to create a release on the **nightly-releases repository**, since that allows non-maintainers to help test the release.
Enter the `tag` `vX.Y.Z-beta1`, to creating pre-release for testing. 
Click `Run workflow`.
The created workflow will run and create a (public) release on the [nightly-releases repository](https://github.com/servo/servo-nightly-builds/releases).
Once the release has been created, you can open a thread on zulip and perform a call for testing of the various artifacts.

### Backporting changes to the release branch

If any critical fixes need to be applied to the release branch (e.g. fixing crashes detected during manual testing), a PR should be opened against the branch following the regular review process.
After that another round of testing should be performed, so try to only backport if absolutely necessary.

###  Preparing the release

Once the test release on the nightly repository has been manually tested, you can prepare the release by running the release workflow again, but this time checking the box to create a release on upstream servo.
This will create only a draft release on the upstream servo repository.
After the artifacts have been uploaded to the release, click on the edit button to edit the draft release.
The tag should already correctly be `vX.Y.Z`.
Change the `target` from `main` to `release/vX.Y.Z`.
Click on `Generate release notes` and then wrap the generated release notes with the following block:

```
<details>
  <summary>Generated Release notes</summary>
  Release notes here.
</details>
```

Contact the dedicated signer of the macOS artifact and ask them to sign the release. 
This might take a while, so this should be done a couple of days before the planned release date.

Finally, add our usual release notes summary, linking to the blog post and to the common issues section (check the previous release notes for examples).
Once the blog post is published, we publish the release.