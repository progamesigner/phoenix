#!/usr/bin/env bash
# Run the Firefox UI smoke tests against the pinned Firefox. Extra args go to pytest.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$("$here/install-firefox.sh")"
python=python3

case "$(uname -s)" in
  Darwin)
    export FIREFOX_BINARY="${FIREFOX_BINARY:-$dest/firefox/Firefox.app/Contents/MacOS/firefox}"
    export GECKODRIVER="${GECKODRIVER:-$dest/geckodriver}"
    ;;
  MINGW* | MSYS* | CYGWIN*)
    # Python on Windows wants Windows paths, and python3 may be the Store stub.
    export FIREFOX_BINARY="${FIREFOX_BINARY:-$(cygpath -w "$dest/firefox/firefox.exe")}"
    export GECKODRIVER="${GECKODRIVER:-$(cygpath -w "$dest/geckodriver.exe")}"
    here="$(cygpath -w "$here")"
    python=python
    ;;
  *)
    export FIREFOX_BINARY="${FIREFOX_BINARY:-$dest/firefox/firefox}"
    export GECKODRIVER="${GECKODRIVER:-$dest/geckodriver}"
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
      exec xvfb-run -a -s "-screen 0 1600x1000x24" python3 -m pytest "$here" "$@"
    fi
    ;;
esac
exec "$python" -m pytest "$here" "$@"
