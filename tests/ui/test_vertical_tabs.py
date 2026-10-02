"""Smoke tests for the toolbar layout with vertical tabs."""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from test_responsive import BREAKPOINT, TOLERANCE, rest_pointer, resize


@pytest.fixture
def vertical_tabs(driver):
    driver.execute_script("Services.prefs.setBoolPref('sidebar.verticalTabs', true)")
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.documentElement.hasAttribute('sidebar-expand-on-hover') || gBrowser.tabContainer.verticalMode")
    )
    yield driver
    driver.execute_script("Services.prefs.setBoolPref('sidebar.verticalTabs', false)")
    WebDriverWait(driver, 5).until(
        lambda d: not d.execute_script("return gBrowser.tabContainer.verticalMode")
    )


def nav_bar_rect(driver):
    return driver.execute_script(
        "const r = document.getElementById('nav-bar').getBoundingClientRect();"
        "return {top: r.top, bottom: r.bottom, width: r.width};"
    )


@pytest.mark.parametrize("width", [BREAKPOINT - 100, BREAKPOINT + 100])
def test_nav_bar_on_screen_with_vertical_tabs(vertical_tabs, width):
    driver = vertical_tabs
    resize(driver, width)
    rest_pointer(driver)

    # With the tabs in the sidebar there is no tab row for the nav bar to
    # overlay, so it must stay in the toolbox at any width.
    def settled(d):
        r = nav_bar_rect(d)
        return r if r["top"] >= -TOLERANCE and r["bottom"] > 0 else False

    rect = WebDriverWait(driver, 5, poll_frequency=0.2).until(settled, message=str(nav_bar_rect(driver)))
    assert rect["width"] > 0
    toolbox_bottom = driver.execute_script("return gNavToolbox.getBoundingClientRect().bottom")
    assert rect["bottom"] <= toolbox_bottom + TOLERANCE
