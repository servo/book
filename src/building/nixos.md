# Building for NixOS

- [Install Nix](https://nixos.org/download), the package manager.
  The easiest way is to use the installer, with either the multi-user or single-user installation (your choice).
- Tell `mach` to use Nix: `export MACH_USE_NIX=`
- Type `nix-shell` to enter a shell with all of the necessary tools and dependencies.
- Install the other dependencies: `./mach bootstrap`
- Build servoshell: `./mach build`

## Troubleshooting

Be sure to look at the [General Troubleshooting](general-troubleshooting.md) section if you have trouble with your build and your problem is not listed below.


<pre><blockquote><samp>error: <a href="https://github.com/NixOS/nix/blob/e3fa7c38d7af8f34de0c24766b2e8cf1cd1330f0/src/libutil/file-system.cc#L164-L184">getting status of</a> /nix/var/nix/daemon-socket/socket: Permission denied</samp></blockquote></pre>

If you get this error and you’ve installed Nix with your system package manager:

- Add yourself to the `nix-users` group
- Log out and log back in

<pre><blockquote><samp>error: <a href="https://github.com/NixOS/nix/blob/e3fa7c38d7af8f34de0c24766b2e8cf1cd1330f0/src/libexpr/eval.cc#L2849">file 'nixpkgs' was not found in the Nix search path (add it using $NIX_PATH or -I)</a></samp></blockquote></pre>

This error is harmless, but you can fix it as follows:

- Run `sudo nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs`
- Run `sudo nix-channel --update`
