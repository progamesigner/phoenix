# Phoenix

<div align="center">

![GitHub Release](https://img.shields.io/github/v/release/progamesigner/phoenix?style=for-the-badge&color=blue)
![GitHub Stars](https://img.shields.io/github/stars/progamesigner/phoenix?style=for-the-badge&color=blue)
![GitHub Contributors](https://img.shields.io/github/contributors/progamesigner/phoenix?style=for-the-badge&color=blue)

A simplified single bar theme for Firefox.

</div>

## Features

- Simplified and minimized single bar theme.

- Feel native to Firefox, with supporting addon theme & colors.

- Multiple alternative options available.

- Support Windows & macOS (Linux support on the roadmap).

### Optional Addons

- [Adaptive Tab Bar Color](https://addons.mozilla.org/en-GB/firefox/addon/adaptive-tab-bar-colour/)

- [Firefox Color](https://addons.mozilla.org/en-US/firefox/addon/firefox-color/)

## Installation

### Enable `userChrome.css`

1. Go to [`about:config`](about:config) page.
2. Click "Accept the Risk and Continue" and search `toolkit.legacyUserProfileCustomizations.stylesheets`.
3. Change the value to `true`.

### Find Firefox Profile Folder

1. Go to [`about:support`](about:support) page.
2. Look for the **Profile Folder** row, and click **Open Folder**.
3. In that folder, create a new folder named `chrome` if it doesn't exist.

### The Easy Way

1. Download the latest version on the [release page](https://github.com/progamesigner/phoenix/releases/latest).
2. Copy everything in the `phoenix_<version>.zip` into your `chrome` folder under Firefox profile folder.
3. Copy `userChrome.example.css` to `userChrome.css`.
4. Edit newly copied `userChrome.css` to add more customization if you want.
5. Restart Firefox.

### The Hard Way

1. Navigate to `chrome` folder of your Firefox profile folder.
```sh
cd your/profile-folder/chrome
```
2. In the terminal, use `git clone` to clone the repository:
```sh
# cd your/profile-folder/chrome
git clone https://github.com/progamesigner/phoenix.git .
cp userChrome.example.css userChrome.css
```
3. Restart Firefox.

## Options

#### Disable Default Stylings
- `phoenix.browser.always-show-fullscreen-toolbars`
- `phoenix.navbar.always-show-navigation-buttons`
- `phoenix.navbar.always-show-navigator-border`
- `phoenix.navbar.hide-window-dragging-area`
- `phoenix.tabbar.always-show-tabs`
- `phoenix.urlbar.always-show-addon-icons` (only has an effect while `phoenix.urlbar.always-show-icons` is off or `phoenix.urlbar.use-dynamic-urlbar-icons` is on; replaces the deprecated `phoenix.navs.always-show-urlbar-icons.always-show-addon-icons`, which still works)
- `phoenix.urlbar.always-show-icons`
- `phoenix.urlbar.hide-leftmost-menu-button`

#### Enable Extra & Alternative Stylings
- `phoenix.browser.use-acrylic-window` (only available on macOS)
- `phoenix.browser.use-rounded-ui` (no effect with the Nova UI, which is already rounded)
- `phoenix.navbar.hide-unified-extensions-button`
- `phoenix.navbar.use-alternative-navigation-buttons`
- `phoenix.navbar.use-conditional-navigation-buttons`
- `phoenix.navbar.use-fade-window-on-inactive`
- `phoenix.navbar.use-grayscale-extension-icons`
- `phoenix.navbar.use-menu-as-private-mode-indicator`
- `phoenix.tabbar.use-more-visible-favicon`
- `phoenix.tabbar.use-tab-loading-indicator`
- `phoenix.tabbar.use-tab-loading-progress-bar`
- `phoenix.urlbar.use-centered-urlbar`
- `phoenix.urlbar.use-connection-type-color-urlbar`
- `phoenix.urlbar.use-container-color-urlbar`
- `phoenix.urlbar.use-dynamic-urlbar-icons`
- `phoenix.urlbar.use-proton-urlbar`
- `phoenix.urlbar.use-transparent-urlbar`

## Compatibility

Phoenix targets Windows & macOS and supports the newest Firefox ESR (currently 153) and the current Firefox release (currently 157). The automated tests run on Linux and Windows against both; see [Development](#development).

## Development

### UI Smoke Tests

`tests/ui` loads the theme into a pinned Firefox (Linux x86_64 or Windows; macOS installs are supported by the scripts but untested) and checks:

- the responsive layout: URL bar and tab strip widths at 699, 701, 1000 and 1001px, that the menu opens after hovering the collapsed toolbar at narrow widths, that the focused URL bar stays centered, that the URL bar fades with the nav bar in narrow windows, and that the Windows window controls stay uncovered;
- the nav bar staying on screen with vertical tabs, on both sides of the breakpoint;
- the find bar text box fitting its container;
- the fullscreen toolbars sliding out and getting an opaque background when shown;
- the content area having no card shadow;
- the window dragging area above the toolbars, and the Windows nav bar gap rule;
- options: `phoenix.browser.use-rounded-ui` (and that it leaves the Nova UI alone) including menu clipping, `phoenix.urlbar.always-show-addon-icons` (including its deprecated name), `phoenix.navbar.hide-window-dragging-area` and the tab loading indicator and progress bar.

On Linux, Firefox needs GTK 3 and ALSA (`libgtk-3-0t64`, `libasound2t64`), and `xvfb` when there is no display.

```sh
pip install -r tests/ui/requirements.txt
tests/ui/run.sh
```

`run.sh` downloads Firefox and geckodriver into `.cache/` on first run (versions pinned in `tests/ui/install-firefox.sh`) and uses `xvfb-run` when no display is available. Set `FIREFOX_VERSION` to test another Firefox build from the Mozilla archive (e.g. `FIREFOX_VERSION=153.4.0esr`), `GECKODRIVER_VERSION` to change geckodriver, `FIREFOX_CACHE_DIR` to move the download cache, or `FIREFOX_BINARY` / `GECKODRIVER` to use your own builds. `UI_NOVA=true` / `UI_NOVA=false` forces `browser.nova.enabled`; unset keeps the browser default.

On failure, full-window screenshots and `geckodriver.log` are written to `.artifacts/ui/` (override with `UI_ARTIFACTS_DIR`).

### CSS Lint

```sh
npm ci
npm run lint:css
```

Runs stylelint plus `scripts/check-css.mjs`, which checks that every `var(--phoenix-*)` is declared, every `@import` target exists and every file under `chrome/` is imported, and that pref media queries use `-moz-pref()` rather than the removed `-moz-bool-pref`.

### CI

`.github/workflows/checks.yaml` runs on pushes to `main`, on pull requests and on manual dispatch:

- `css-lint` runs the CSS lint above.
- `ui-smoke` runs on Linux and Windows against the newest Firefox release (with the Nova UI on and off) and the newest ESR, using the versions pinned in the workflow; the Windows runs cover the `-moz-platform: windows` rules. On Linux it also runs `scripts/check-firefox-vars.mjs` against each Firefox (checks that the Firefox CSS variables the theme reads or overrides still exist there). When it fails, the screenshots, `pytest.log`, `junit.xml` and `geckodriver.log` are uploaded as a `ui-smoke-failure-<Linux|Windows>-<Firefox version>[-nova-<true|false>]` artifact.

`.github/workflows/release.yaml` runs when a `v*` tag is pushed: it builds `phoenix_<tag>.zip` with `git archive` (files marked `export-ignore` in `.gitattributes` are left out) and attaches it to a new GitHub release.
