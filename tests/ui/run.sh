#!/usr/bin/env bash
# Run the Firefox UI smoke tests against the pinned Firefox. Extra args go to pytest.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$("$here/install-firefox.sh")"

export FIREFOX_BINARY="${FIREFOX_BINARY:-$dest/firefox/firefox}"
export GECKODRIVER="${GECKODRIVER:-$dest/geckodriver}"

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  exec xvfb-run -a -s "-screen 0 1600x1000x24" python3 -m pytest "$here" "$@"
fi
exec python3 -m pytest "$here" "$@"
