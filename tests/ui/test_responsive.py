"""Smoke tests for the responsive toolbar layout around the 1000px breakpoint.

`phoenix-responsiveness.css` collapses the tab strip and overlays the nav bar
at `(max-width: 1000px)`. 699/701 sit on either side of the previous 700px
breakpoint, 1000/1001 on either side of the current one.
"""

import pytest
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BREAKPOINT = 1000
WIDTHS = [699, 701, 1000, 1001]
NARROW_WIDTHS = [w for w in WIDTHS if w <= BREAKPOINT]
WINDOW_HEIGHT = 700
TOLERANCE = 1

RECT_IDS = ["nav-bar", "urlbar-container", "urlbar", "TabsToolbar", "tabbrowser-tabs"]


def resize(driver, width):
    """Resize so the chrome document (what the media queries see) is `width` wide."""
    driver.execute_script(
        "window.resizeTo(arguments[0] + window.outerWidth - window.innerWidth, arguments[1])",
        width,
        WINDOW_HEIGHT,
    )
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return window.innerWidth") == width
    )


def rest_pointer(driver):
    """Park the pointer over web content and move focus there, so the toolbox is idle."""
    content = driver.find_element(By.ID, "tabbrowser-tabpanels")
    ActionChains(driver).move_to_element(content).perform()
    driver.execute_script("gBrowser.selectedBrowser.focus()")


def snapshot(driver):
    return driver.execute_script(
        """
        const rects = {};
        for (const id of arguments[0]) {
          const el = document.getElementById(id);
          const r = el.getBoundingClientRect();
          rects[id] = {
            left: r.left, right: r.right, top: r.top, width: r.width,
            opacity: getComputedStyle(el).opacity,
          };
        }
        rects.tabs = [...gBrowser.tabs].map(tab => ({
          selected: tab.selected,
          width: tab.getBoundingClientRect().width,
          display: getComputedStyle(tab).display,
        }));
        return rects;
        """,
        RECT_IDS,
    )


def settled_snapshot(driver, timeout=5):
    """Wait for width/opacity transitions to finish before measuring."""
    state = {"prev": None}

    def stable(d):
        cur = snapshot(d)
        done = cur == state["prev"]
        state["prev"] = cur
        return cur if done else False

    return WebDriverWait(driver, timeout, poll_frequency=0.2).until(stable)


def opacity(driver, element_id):
    return driver.execute_script(
        "return getComputedStyle(document.getElementById(arguments[0])).opacity",
        element_id,
    )


@pytest.fixture(scope="module")
def two_tabs(driver):
    driver.execute_script(
        """
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        while (gBrowser.tabs.length < 2) {
          gBrowser.addTab("about:blank", { triggeringPrincipal: principal });
        }
        gBrowser.selectedTab = gBrowser.tabs[0];
        """
    )
    return driver


@pytest.mark.parametrize("width", WIDTHS)
def test_urlbar_and_tabs_width(two_tabs, width):
    driver = two_tabs
    resize(driver, width)
    rest_pointer(driver)
    s = settled_snapshot(driver)

    narrow = driver.execute_script(
        "return matchMedia(`(max-width: ${arguments[0]}px)`).matches", BREAKPOINT
    )
    assert narrow == (width <= BREAKPOINT)

    nav, urlbar, tabs_toolbar = s["nav-bar"], s["urlbar"], s["TabsToolbar"]

    # The address bar always fits on screen and within the nav bar.
    assert urlbar["width"] > 0
    assert urlbar["left"] >= nav["left"] - TOLERANCE
    assert urlbar["right"] <= min(nav["right"], width) + TOLERANCE
    assert tabs_toolbar["right"] <= width + TOLERANCE

    if narrow:
        # Both bars span the window and are stacked on the same row.
        assert nav["width"] == pytest.approx(width, abs=TOLERANCE)
        assert tabs_toolbar["width"] == pytest.approx(width, abs=TOLERANCE)
        assert nav["top"] == pytest.approx(tabs_toolbar["top"], abs=TOLERANCE)

        # Idle: tab title shown, nav bar faded out.
        assert s["nav-bar"]["opacity"] == "0"
        assert s["tabbrowser-tabs"]["opacity"] == "1"

        # Only the selected tab is rendered.
        for tab in s["tabs"]:
            if tab["selected"]:
                assert tab["display"] != "none"
                assert 0 < tab["width"] <= width
            else:
                assert tab["display"] == "none"
    else:
        # Nav bar and tab strip sit side by side, tab strip flush right.
        assert nav["top"] == pytest.approx(tabs_toolbar["top"], abs=TOLERANCE)
        assert nav["right"] <= tabs_toolbar["left"] + TOLERANCE
        assert tabs_toolbar["right"] == pytest.approx(width, abs=TOLERANCE)

        # --phoenix-urlbar-collapsed-width, capped by --phoenix-single-tab-width.
        assert s["urlbar-container"]["width"] >= min(360, width - 800) - TOLERANCE

        assert s["nav-bar"]["opacity"] == "1"
        assert s["tabbrowser-tabs"]["opacity"] == "1"
        assert all(tab["display"] != "none" and tab["width"] > 0 for tab in s["tabs"])


@pytest.mark.parametrize("width", NARROW_WIDTHS)
def test_narrow_menu_opens_after_hover(two_tabs, width):
    driver = two_tabs
    resize(driver, width)
    rest_pointer(driver)
    wait = WebDriverWait(driver, 5, poll_frequency=0.1)
    wait.until(lambda d: opacity(d, "nav-bar") == "0")

    # Slide the pointer into the toolbar area: the nav bar fades in over the tabs.
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "TabsToolbar")).perform()
    wait.until(lambda d: opacity(d, "nav-bar") == "1")
    wait.until(lambda d: opacity(d, "tabbrowser-tabs") == "0")

    # The menu button must be the topmost element where the pointer lands.
    button = driver.find_element(By.ID, "PanelUI-menu-button")
    hit = driver.execute_script(
        """
        const r = arguments[0].getBoundingClientRect();
        const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        return el && (el === arguments[0] || arguments[0].contains(el));
        """,
        button,
    )
    assert hit, "menu button is covered by another element"

    ActionChains(driver).move_to_element(button).click().perform()
    try:
        wait.until(
            lambda d: d.execute_script(
                "return document.getElementById('appMenu-popup').state"
            )
            == "open"
        )
    finally:
        driver.execute_script("PanelUI.hide()")
        wait.until(
            lambda d: d.execute_script(
                "return document.getElementById('appMenu-popup').state"
            )
            == "closed"
        )


@pytest.mark.parametrize("width", NARROW_WIDTHS)
def test_narrow_urlbar_fades(two_tabs, width):
    driver = two_tabs
    resize(driver, width)
    rest_pointer(driver)
    wait = WebDriverWait(driver, 5, poll_frequency=0.1)
    fading = """
        return [gURLBar, gURLBar.querySelector('.urlbar-input-container')].map(el => {
          const cs = getComputedStyle(el);
          const props = cs.transitionProperty.split(', ');
          const durations = cs.transitionDuration.split(', ');
          const i = props.indexOf('opacity');
          return [i >= 0 && parseFloat(durations[i % durations.length]) > 0, cs.opacity];
        });
    """

    # The address bar fades along with the nav bar rather than popping in and out.
    wait.until(lambda d: d.execute_script(fading) == [[True, "0"], [True, "0"]])
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "TabsToolbar")).perform()
    wait.until(lambda d: d.execute_script(fading) == [[True, "1"], [True, "1"]])
    rest_pointer(driver)
    wait.until(lambda d: d.execute_script(fading) == [[True, "0"], [True, "0"]])


@pytest.mark.parametrize("width", [800, 1400])
def test_focused_urlbar_is_centered(driver, width):
    resize(driver, width)
    driver.execute_script(
        'gURLBar.focus(); gURLBar.value = "example"; gURLBar.startQuery()'
    )
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return gURLBar.hasAttribute('popover-open')")
    )
    urlbar = driver.execute_script(
        "const r = gURLBar.getBoundingClientRect(); return {left: r.left, width: r.width}"
    )
    assert urlbar["left"] + urlbar["width"] / 2 == pytest.approx(width / 2, abs=TOLERANCE)
    driver.execute_script("gURLBar.view.close(); gBrowser.selectedBrowser.focus()")
