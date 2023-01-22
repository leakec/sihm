class Sihm < Formula
  desc "Standalone interactive HTML movie (SIHM)"
  homepage "https://github.com/leakec/sihm"
  version "0.0.2"

  # Empty dummy URL to make brew happy
  url "file:///dev/null"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

  depends_on "yarn"
  depends_on "node"
  depends_on "cmake"
  depends_on "make"
  depends_on "sihm" => :python
end
