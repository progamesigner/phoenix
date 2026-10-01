import os
import re
import shutil
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = Path(os.environ.get("UI_ARTIFACTS_DIR", REPO_ROOT / ".artifacts" / "ui"))


def _install_theme(profile_dir: Path) -> None:
    # Mirror "The Hard Way" install: the repository becomes <profile>/chrome.
    chrome_dir = profile_dir / "chrome"
    shutil.copytree(REPO_ROOT / "chrome", chrome_dir / "chrome")
    shutil.copy(REPO_ROOT / "userChrome.example.css", chrome_dir / "userChrome.css")


@pytest.fixture(scope="session")
def driver(tmp_path_factory):
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    profile_dir = tmp_path_factory.mktemp("profile")
    _install_theme(profile_dir)

    options = Options()
    if binary := os.environ.get("FIREFOX_BINARY"):
        options.binary_location = binary
    options.add_argument("-profile")
    options.add_argument(str(profile_dir))
    options.set_preference("toolkit.legacyUserProfileCustomizations.stylesheets", True)
    options.set_preference("browser.aboutwelcome.enabled", False)
    options.set_preference("browser.startup.homepage_override.mstone", "ignore")
    options.set_preference("sidebar.verticalTabs", False)

    # Chrome-context scripts need system access (geckodriver 0.36+, Firefox 138+).
    service = Service(
        executable_path=os.environ.get("GECKODRIVER"),
        service_args=["--allow-system-access"],
        log_output=str(ARTIFACTS_DIR / "geckodriver.log"),
    )
    drv = webdriver.Firefox(options=options, service=service)
    drv.set_context(drv.CONTEXT_CHROME)
    WebDriverWait(drv, 10).until(
        lambda d: d.execute_script("return !!document.getElementById('nav-bar')")
    )
    yield drv
    drv.quit()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    drv = item.funcargs.get("driver")
    if report.failed and drv is not None:
        # In chrome context this captures the whole browser window, toolbars included.
        name = re.sub(r"[^\w.-]+", "_", item.nodeid)
        path = ARTIFACTS_DIR / f"{name}-{report.when}.png"
        try:
            drv.get_screenshot_as_file(str(path))
            report.sections.append(("screenshot", str(path)))
        except Exception as exc:  # the browser may be gone
            report.sections.append(("screenshot", f"failed: {exc}"))
    return report
