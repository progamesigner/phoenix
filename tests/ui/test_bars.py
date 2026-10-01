"""Smoke tests for the find bar and the auto-hiding fullscreen toolbars."""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

TOLERANCE = 1


def rect(driver, script):
    return driver.execute_script(
        f"const r = ({script}).getBoundingClientRect();"
        "return {top: r.top, bottom: r.bottom, height: r.height};"
    )


@pytest.fixture
def findbar(driver):
    driver.execute_script("gLazyFindCommand('onFindCommand')")
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script(
            "const f = gBrowser.getCachedFindBar(); return !!f && !f.hidden"
        )
    )
    yield driver
    driver.execute_script("gBrowser.getCachedFindBar().close(true)")


def test_findbar_textbox_fits_container(findbar):
    driver = findbar
    container = rect(driver, "gBrowser.getCachedFindBar().querySelector('.findbar-container')")
    field = rect(driver, "gBrowser.getCachedFindBar()._findField")
    # Nova raises Firefox's own container height to 32px; the padded box must grow with it.
    base = driver.execute_script(
        """
        const c = gBrowser.getCachedFindBar().querySelector('.findbar-container');
        const v = getComputedStyle(c).getPropertyValue('--findbar-container-height').trim();
        return v ? parseFloat(v) : 28;
        """
    )
    assert container["height"] == pytest.approx(base + 2 * 8, abs=TOLERANCE)
    assert field["top"] >= container["top"] - TOLERANCE
    assert field["bottom"] <= container["bottom"] + TOLERANCE


@pytest.fixture
def fullscreen(driver):
    driver.execute_script("window.fullScreen = true")
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.documentElement.hasAttribute('inFullscreen')")
    )
    yield driver
    driver.execute_script("window.fullScreen = false")
    WebDriverWait(driver, 5).until(
        lambda d: not d.execute_script("return document.documentElement.hasAttribute('inFullscreen')")
    )


def test_fullscreen_toolbars_slide_out(fullscreen):
    driver = fullscreen
    driver.execute_script("gBrowser.selectedBrowser.focus()")
    wait = WebDriverWait(driver, 5, poll_frequency=0.2)
    wait.until(lambda d: rect(d, "gNavToolbox")["bottom"] <= TOLERANCE)
    wait.until(lambda d: rect(d, "gURLBar")["bottom"] <= TOLERANCE)


def test_fullscreen_toolbars_overlay_is_opaque(fullscreen):
    driver = fullscreen
    driver.execute_script("gURLBar.focus()")
    WebDriverWait(driver, 5, poll_frequency=0.2).until(
        lambda d: rect(d, "gNavToolbox")["top"] >= -TOLERANCE
    )
    # The toolbox overlays the page in fullscreen, so it needs a background of its own.
    background = driver.execute_script(
        "const s = getComputedStyle(gNavToolbox); return [s.backgroundColor, s.backgroundImage]"
    )
    driver.execute_script("gBrowser.selectedBrowser.focus()")
    assert background != ["rgba(0, 0, 0, 0)", "none"]
