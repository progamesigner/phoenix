"""Selector checks for platform-gated rules in `phoenix-platforms.css`.

CI runs on Linux, where `(-moz-platform: windows)` never matches, so these
tests read the shipped rule out of the loaded stylesheet and evaluate its
selector with `Element.matches()` instead of checking computed styles.
"""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

# Resolves the Windows nav bar gap rule from the live CSSOM, expanding `&` if the
# rule is ever nested again, and reports whether #nav-bar matches it.
NAV_BAR_GAP_MATCHES = """
function* walk(rules) {
  for (const rule of rules) {
    yield rule;
    if (rule instanceof CSSImportRule) {
      if (rule.styleSheet) yield* walk(rule.styleSheet.cssRules);
    } else if (rule.cssRules) {
      yield* walk(rule.cssRules);
    }
  }
}
function selectorOf(rule) {
  const parent = rule.parentRule;
  if (!(parent instanceof CSSStyleRule)) return rule.selectorText;
  return rule.selectorText.replaceAll('&', `:is(${selectorOf(parent)})`);
}
const userSheet = InspectorUtils.getAllStyleSheets(document, false, false)
  .find(s => s.href?.endsWith('/userChrome.css'));
const windows = [...walk(userSheet.cssRules)].filter(r =>
  r instanceof CSSMediaRule &&
  r.parentStyleSheet.href.endsWith('/phoenix-platforms.css') &&
  /-moz-platform:\\s*windows/.test(r.conditionText));
const rules = windows.flatMap(m => [...walk(m.cssRules)]).filter(r =>
  r instanceof CSSStyleRule && r.style.marginLeft === '2px' &&
  /^&|#nav-bar/.test(r.selectorText));
if (rules.length !== 1) throw new Error(`expected one nav bar gap rule, found ${rules.length}`);
return document.getElementById('nav-bar').matches(selectorOf(rules[0]));
"""


def first_item(driver):
    return driver.execute_script(
        "const c = CustomizableUI.getCustomizationTarget(document.getElementById('nav-bar'))"
        ".firstElementChild;"
        "return c.localName === 'toolbarpaletteitem' ? c.firstElementChild.id : c.id"
    )


def palette_wrapped(driver):
    return driver.execute_script(
        "return !!document.querySelector('#nav-bar-customization-target > toolbarpaletteitem')"
    )


@pytest.fixture
def nav_bar_first(driver, request):
    """Move the widget given as the param to the start of the nav bar, then restore the order."""
    placements = driver.execute_script("return CustomizableUI.getWidgetIdsInArea('nav-bar')")
    driver.execute_script("CustomizableUI.moveWidgetWithinArea(arguments[0], 0)", request.param)
    yield request.param
    driver.execute_script(
        "arguments[0].forEach((id, i) => CustomizableUI.moveWidgetWithinArea(id, i))", placements
    )


@pytest.fixture
def customizing(driver):
    driver.execute_script("gCustomizeMode.enter()")
    WebDriverWait(driver, 10).until(palette_wrapped)
    yield driver
    driver.execute_script("gCustomizeMode.exit()")
    WebDriverWait(driver, 10).until(
        lambda d: not palette_wrapped(d)
        and not d.execute_script("return document.documentElement.hasAttribute('customizing')")
    )


CASES = pytest.mark.parametrize(
    "nav_bar_first, gap",
    [("back-button", True), ("urlbar-container", False)],
    indirect=["nav_bar_first"],
)


@CASES
def test_windows_nav_bar_gap_follows_first_item(driver, nav_bar_first, gap):
    assert first_item(driver) == nav_bar_first
    assert driver.execute_script(NAV_BAR_GAP_MATCHES) is gap


@CASES
def test_windows_nav_bar_gap_follows_first_item_while_customizing(
    driver, nav_bar_first, customizing, gap
):
    assert first_item(driver) == nav_bar_first
    assert driver.execute_script(NAV_BAR_GAP_MATCHES) is gap
