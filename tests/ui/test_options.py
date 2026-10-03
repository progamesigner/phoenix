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
