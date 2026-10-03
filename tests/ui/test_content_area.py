"""Smoke tests for the content area framing."""


def test_content_area_has_no_shadow(driver):
    # Firefox frames the page with a card shadow when the revamped sidebar is
    # on (always, as of Firefox 157); Phoenix keeps the page flush with the bar.
    if not driver.execute_script("return Services.prefs.getBoolPref('sidebar.revamp', false)"):
        return
    shadow = driver.execute_script(
        "return getComputedStyle(gBrowser.selectedBrowser.closest('.browserContainer')).boxShadow"
    )
    assert shadow == "none"
