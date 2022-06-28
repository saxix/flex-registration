import contextlib
from collections import namedtuple

import pytest
from selenium.webdriver.common.by import By

from testutils.utils import wait_for

Proxy = namedtuple("Proxy", "host,port")


def pytest_configure(config):
    if not config.option.driver:
        setattr(config.option, "driver", "chrome")


SELENIUM_DEFAULT_PAGE_LOAD_TIMEOUT = 3
SELENIUM_DEFAULT_IMPLICITLY_WAIT = 1
SELENIUM_DEFAULT_SCRIPT_TIMEOUT = 1


@contextlib.contextmanager
def timeouts(driver, wait=None, page=None, script=None):
    from selenium.webdriver.common.timeouts import Timeouts

    _current: Timeouts = driver.timeouts
    if wait:
        driver.implicitly_wait(wait)
    if page:
        driver.set_page_load_timeout(page)
    if script:
        driver.set_script_timeout(script)
    yield
    driver.timeouts = _current


def set_input_value(driver, *args):
    rules = args[:-1]
    el = driver.find_element(*rules)
    el.clear()
    el.send_keys(args[-1])


def find_by_css(selenium, *args):
    return wait_for(selenium, By.CSS_SELECTOR, *args)


@pytest.fixture
def chrome_options(request):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    if not request.config.getvalue("show_browser"):
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

    return chrome_options


@pytest.fixture
def selenium(monkeypatch, settings, driver):
    settings.CAPTCHA_TEST_MODE = True
    monkeypatch.setattr("django.conf.settings.CAPTCHA_TEST_MODE", True)
    monkeypatch.setattr("captcha.conf.settings.CAPTCHA_TEST_MODE", True)
    driver.with_timeouts = timeouts.__get__(driver)
    driver.set_input_value = set_input_value.__get__(driver)

    driver.wait_for = wait_for.__get__(driver)
    driver.find_by_css = find_by_css.__get__(driver)

    yield driver
