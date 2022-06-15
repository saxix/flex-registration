import time
from functools import partial
from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from smart_register.core.models import Validator
from testutils.utils import wait_for


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # ./manage.py dumpdata core registration i18n > tests/browser/fixtures.json
        call_command("loaddata", Path(__file__).parent / "fixtures.json")


@pytest.fixture()
def registration(db):
    from smart_register.core.models import FlexForm
    from smart_register.registration.models import Registration

    form = FlexForm.objects.get(name="Intro uk-ua")
    rec, __ = Registration.objects.update_or_create(slug="test1",
                                                    defaults=dict(name="aaa",
                                                                  title="Test",
                                                                  flex_form=form,
                                                                  active=True,
                                                                  locale="uk-ua",
                                                                  locales=['uk-ua', 'en-us'],
                                                                  unique_field='pk',
                                                                  unique_field_error='Duplicated pk')
                                                    )
    rec.scripts.set([Validator.objects.get(name='onsubmit')])
    return rec


@pytest.fixture()
def url(registration):
    return '/uk-ua/register/test1/'
    return reverse("register", args=[registration.locale, registration.slug])


@pytest.mark.selenium
def test_ukr(live_server, selenium, url):
    assert settings.CAPTCHA_TEST_MODE

    selenium.implicitly_wait(3)
    selenium.get(f"{live_server.url}{url}")
    dim = selenium.get_window_size()
    selenium.set_window_size(1100, dim["height"])
    find_by_css = partial(wait_for, selenium, By.CSS_SELECTOR)

    wait_for(selenium, By.CSS_SELECTOR, "label[for=id_household-0-residence_status_h_c_0]").click()
    wait_for(selenium, By.CSS_SELECTOR, "input[type=submit]").click()
    #
    LOCATIONS = ["Автономна Республіка Крим", "Бахчисарайський", "Ароматненська"]
    find_by_css("fieldset.admin1_h_c .select2 .selection .select2-selection").click()
    find_by_css(".select2-search__field").send_keys(LOCATIONS[0])
    time.sleep(2)
    find_by_css(".select2-search__field").send_keys(Keys.ENTER)
    time.sleep(2)
    select = Select(selenium.find_element(By.CSS_SELECTOR, "select[name=household-0-admin1_h_c]"))
    assert select.first_selected_option.text == LOCATIONS[0]

    find_by_css("fieldset.admin2_h_c .select2 .selection .select2-selection").click()
    find_by_css(".select2-search__field").send_keys(LOCATIONS[1])
    time.sleep(2)
    find_by_css(".select2-search__field").send_keys(Keys.ENTER)
    time.sleep(2)
    select = Select(selenium.find_element(By.CSS_SELECTOR, "select[name=household-0-admin2_h_c]"))
    assert select.first_selected_option.text == LOCATIONS[1]

    find_by_css("fieldset.admin3_h_c .select2 .selection .select2-selection").click()
    find_by_css(".select2-search__field").send_keys(LOCATIONS[2])
    time.sleep(2)
    find_by_css(".select2-search__field").send_keys(Keys.ENTER)
    time.sleep(5)
    wait_for(selenium, By.CSS_SELECTOR, "select[name=household-0-admin3_h_c]")
    select = Select(selenium.find_element(By.CSS_SELECTOR, "select[name=household-0-admin3_h_c]"))
    assert select.first_selected_option.text == LOCATIONS[2]

    wait_for(selenium, By.CSS_SELECTOR, "input[type=submit]").click()

    find_by_css("input[name=household-0-size_h_c").send_keys("1")
    find_by_css('input[name="individuals-0-given_name_i_c"]').send_keys("Given Name")
    find_by_css('input[name="individuals-0-family_name_i_c"]').send_keys("Family Name")
    find_by_css('input[name="individuals-0-middle_name_i_c"]').send_keys("Middle Name")
    find_by_css('input[name="individuals-0-gender_i_c"]').click()

    find_by_css('input[name="individuals-0-birth_date"]').send_keys("2000-12-01")

    select = Select(selenium.find_element(By.CSS_SELECTOR, 'select[name="individuals-0-relationship_i_c"]'))
    select.select_by_visible_text("Особисто голова домогосподарства")

    find_by_css('input[name="marketing-0-captcha_1"]').send_keys("passed")
    wait_for(selenium, By.CSS_SELECTOR, "input[type=submit]").click()

    find_by_css(f"a[href='{url}']").click()
