with import (builtins.fetchTarball {
  url = "https://github.com/NixOS/nixpkgs/archive/b06025f1533a1e07b6db3e75151caa155d1c7eb3.tar.gz";
}) {};
stdenv.mkDerivation rec {
  name = "servo-book-env";
  buildInputs = [ mdbook mdbook-mermaid ];
}
