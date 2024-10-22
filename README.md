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
- `phoenix.navbar.always-show-navigation-buttons`
- `phoenix.navbar.always-show-navigator-border`
- `phoenix.navbar.hide-unified-extensions-button`
- `phoenix.navbar.hide-window-dragging-area`
- `phoenix.tabbar.always-show-all-tabs-button`
- `phoenix.tabbar.always-show-tabs`
- `phoenix.urlbar.always-show-icons`
- `phoenix.urlbar.hide-leftmost-menu-button`

#### Enable Extra & Alternative Stylings
- `phoenix.navbar.use-alternative-navigation-buttons`
- `phoenix.navbar.use-conditional-navigation-buttons`
- `phoenix.navbar.use-fade-window-on-inactive`
- `phoenix.navbar.use-grayscale-extension-icons`
- `phoenix.navbar.use-menu-as-private-mode-indicator`
- `phoenix.urlbar.use-centered-urlbar`
- `phoenix.urlbar.use-connection-type-color-urlbar`
- `phoenix.urlbar.use-dynamic-urlbar-icons`
- `phoenix.urlbar.use-proton-urlbar`
- `phoenix.urlbar.use-transparent-urlbar`

## Compatibility

Currently tested on Windows & macOS with Firefox 131+
