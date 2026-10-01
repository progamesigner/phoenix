#!/usr/bin/env bash
# Download the pinned Firefox and geckodriver used by the UI smoke tests (Linux x86_64).
# Prints the install directory; binaries are <dir>/firefox/firefox and <dir>/geckodriver.
set -euo pipefail

FIREFOX_VERSION="${FIREFOX_VERSION:-156.0.1}"
GECKODRIVER_VERSION="${GECKODRIVER_VERSION:-0.37.1}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
dest="${FIREFOX_CACHE_DIR:-$root/.cache}/firefox-${FIREFOX_VERSION}_geckodriver-${GECKODRIVER_VERSION}"

if [[ ! -x "$dest/firefox/firefox" || ! -x "$dest/geckodriver" ]]; then
  mkdir -p "$dest"
  curl -fsSL "https://ftp.mozilla.org/pub/firefox/releases/${FIREFOX_VERSION}/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.xz" \
    | tar -xJ -C "$dest"
  curl -fsSL "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" \
    | tar -xz -C "$dest"
fi

echo "$dest"
