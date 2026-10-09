#!/usr/bin/env bash
# Download the pinned Firefox and geckodriver used by the UI smoke tests.
# FIREFOX_VERSION is a release from https://ftp.mozilla.org/pub/firefox/releases/
# (e.g. 157.0.1 or 153.4.0esr).
# Prints the install directory; the Firefox install dir is <dir>/firefox and the
# driver is <dir>/geckodriver (both with .exe on Windows, see run.sh).
set -euo pipefail

FIREFOX_VERSION="${FIREFOX_VERSION:-157.0.1}"
GECKODRIVER_VERSION="${GECKODRIVER_VERSION:-0.37.1}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
dest="${FIREFOX_CACHE_DIR:-$root/.cache}/firefox-${FIREFOX_VERSION}_geckodriver-${GECKODRIVER_VERSION}"
firefox_url="https://ftp.mozilla.org/pub/firefox/releases/${FIREFOX_VERSION}"
geckodriver_url="https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}"

case "$(uname -s)" in
  Linux)
    firefox_bin="$dest/firefox/firefox"
    geckodriver_bin="$dest/geckodriver"
    ;;
  Darwin)
    firefox_bin="$dest/firefox/Firefox.app/Contents/MacOS/firefox"
    geckodriver_bin="$dest/geckodriver"
    ;;
  MINGW* | MSYS* | CYGWIN*)
    firefox_bin="$dest/firefox/firefox.exe"
    geckodriver_bin="$dest/geckodriver.exe"
    ;;
  *)
    echo "unsupported platform: $(uname -s)" >&2
    exit 1
    ;;
esac

fetch() {
  curl -fsSL --retry 5 --retry-all-errors -o "$1" "$2"
}

# omni.ja holds Firefox's chrome; a cut-off download shows up there first. unzip
# warns about the jar's optimized layout and exits 2 even when the data is fine.
check_omni() {
  for jar in "$1/omni.ja" "$1/browser/omni.ja"; do
    if ! { unzip -tq "$jar" 2>/dev/null || true; } | grep "^No errors detected" > /dev/null; then
      echo "$jar is damaged" >&2
      return 1
    fi
  done
}

if [[ ! -x "$firefox_bin" || ! -x "$geckodriver_bin" ]]; then
  # Build next to the cache entry and move it into place only once it is complete,
  # so an interrupted or truncated download never looks installed.
  mkdir -p "$(dirname "$dest")"
  tmp="$(mktemp -d "$dest.XXXXXX")"
  trap 'rm -rf "$tmp"' EXIT
  case "$(uname -s)" in
    Linux)
      fetch "$tmp/firefox.tar.xz" "$firefox_url/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.xz"
      xz -t "$tmp/firefox.tar.xz"
      tar -xJf "$tmp/firefox.tar.xz" -C "$tmp"
      check_omni "$tmp/firefox"
      fetch "$tmp/geckodriver.tar.gz" "${geckodriver_url}-linux64.tar.gz"
      tar -xzf "$tmp/geckodriver.tar.gz" -C "$tmp"
      rm "$tmp/firefox.tar.xz" "$tmp/geckodriver.tar.gz"
      ;;
    Darwin)
      arch=""
      [[ "$(uname -m)" == arm64 ]] && arch="-aarch64"
      fetch "$tmp/firefox.dmg" "$firefox_url/mac/en-US/Firefox%20${FIREFOX_VERSION}.dmg"
      mnt="$(mktemp -d)"
      hdiutil attach -quiet -nobrowse -readonly -mountpoint "$mnt" "$tmp/firefox.dmg"
      mkdir -p "$tmp/firefox"
      cp -R "$mnt/Firefox.app" "$tmp/firefox/"
      hdiutil detach -quiet "$mnt"
      check_omni "$tmp/firefox/Firefox.app/Contents/Resources"
      fetch "$tmp/geckodriver.tar.gz" "${geckodriver_url}-macos${arch}.tar.gz"
      tar -xzf "$tmp/geckodriver.tar.gz" -C "$tmp"
      rm "$tmp/firefox.dmg" "$tmp/geckodriver.tar.gz"
      ;;
    *)
      # The full installer is a 7-Zip self-extracting archive; its core/ folder
      # is a complete Firefox install, so extract it instead of installing.
      # 7-Zip is a native program, so hand it Windows paths; it fails on a
      # truncated archive.
      sevenzip="$(command -v 7z || echo "/c/Program Files/7-Zip/7z.exe")"
      win_tmp="$(cygpath -w "$tmp")"
      fetch "$tmp/setup.exe" "$firefox_url/win64/en-US/Firefox%20Setup%20${FIREFOX_VERSION}.exe"
      "$sevenzip" x -y -bd -o"$win_tmp\\setup" "$win_tmp\\setup.exe" > /dev/null
      mv "$tmp/setup/core" "$tmp/firefox"
      fetch "$tmp/geckodriver.zip" "${geckodriver_url}-win64.zip"
      "$sevenzip" x -y -bd -o"$win_tmp" "$win_tmp\\geckodriver.zip" > /dev/null
      rm -rf "$tmp/setup" "$tmp/setup.exe" "$tmp/geckodriver.zip"
      ;;
  esac
  rm -rf "$dest"
  mv "$tmp" "$dest"
  trap - EXIT
fi

echo "$dest"
