// Restore session
user_pref("browser.startup.page", 3);

// Disable warning on about:config
user_pref("browser.aboutConfig.showWarning", false);

// Disable warning on quit (macOS)
user_pref("browser.warnOnQuitShortcut", false);

// Enable userChrome.css
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Enable remote debugging
user_pref("devtools.debugger.remote-enabled", true);
user_pref("devtools.chrome.enabled", true);
user_pref("devtools.debugger.prompt-connection", false);
