"""Smoke tests for optional stylings toggled through phoenix.* prefs."""

import pytest
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture
def pref(driver):
    """Set boolean prefs for one test; pref media queries re-evaluate live."""
    names = []

    def set_pref(name, value):
        names.append(name)
        driver.execute_script("Services.prefs.setBoolPref(arguments[0], arguments[1])", name, value)

    yield set_pref
    for name in names:
        driver.execute_script("Services.prefs.clearUserPref(arguments[0])", name)


def tab_radius(driver):
    return driver.execute_script(
        "return getComputedStyle(gBrowser.selectedTab.querySelector('.tab-background')).borderRadius"
    )


def test_rounded_ui_only_without_nova(driver, pref):
    nova = driver.execute_script("return Services.prefs.getBoolPref('browser.nova.enabled', false)")
    default = tab_radius(driver)

    pref("phoenix.browser.use-rounded-ui", True)
    if nova:
        # Nova is already rounded; the option must leave its styling alone.
        assert tab_radius(driver) == default
    else:
        WebDriverWait(driver, 5).until(lambda d: tab_radius(d) == "30px")


def dragging_area(driver):
    return driver.execute_script(
        """
        return {
          height: getComputedStyle(document.documentElement)
            .getPropertyValue('--phoenix-window-dragging-area-height').trim(),
          navBarMargin: getComputedStyle(document.getElementById('nav-bar')).marginTop,
        };
        """
    )


@pytest.fixture
def custom_titlebar(driver):
    """Let Firefox draw the tabs in the titlebar, in a restored window.

    Linux only allows it with GTK client-side decorations, which Xvfb lacks,
    so pretend the system supports it and let Firefox set its own attribute.
    """
    supported = driver.execute_script(
        """
        const supported = CustomTitlebar.systemSupported;
        Object.defineProperty(CustomTitlebar, 'systemSupported', {configurable: true, value: true});
        Services.prefs.setIntPref('browser.tabs.inTitlebar', 1);
        CustomTitlebar._update();
        if (window.windowState != window.STATE_NORMAL) window.restore();
        return supported;
        """
    )
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return window.windowState == window.STATE_NORMAL")
    )
    yield
    driver.execute_script(
        """
        Object.defineProperty(CustomTitlebar, 'systemSupported', {configurable: true, value: arguments[0]});
        Services.prefs.clearUserPref('browser.tabs.inTitlebar');
        CustomTitlebar._update();
        """,
        supported,
    )


def test_window_dragging_area(driver, custom_titlebar, pref):
    WebDriverWait(driver, 5).until(
        lambda d: dragging_area(d) == {"height": "4px", "navBarMargin": "4px"}
    )

    pref("phoenix.navbar.hide-window-dragging-area", True)
    WebDriverWait(driver, 5).until(
        lambda d: dragging_area(d) == {"height": "0px", "navBarMargin": "0px"}
    )
