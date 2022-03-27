import time
from functools import partial
from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import call_command
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from testutils.utils import wait_for


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", Path(__file__).parent / "fixtures.json")


@pytest.fixture()
def registration(db):
    from smart_register.core.models import FlexForm
    from smart_register.registration.models import Registration

    form = FlexForm.objects.get(name="Intro uk-ua")
    return Registration.objects.create(
        name="aaa", slug="aaa", title="Test", flex_form=form, active=True, locale="uk-ua"
    )


@pytest.mark.selenium
def test_ukr(live_server, selenium, registration):
    assert settings.CAPTCHA_TEST_MODE

    selenium.implicitly_wait(3)
    selenium.get(f"{live_server.url}{registration.get_absolute_url()}")
    dim = selenium.get_window_size()
    selenium.set_window_size(1100, dim["height"])
    find_by_css = partial(wait_for, selenium, By.CSS_SELECTOR)

    wait_for(selenium, By.CSS_SELECTOR, "label[for=id_household-0-residence_status_h_c_0]").click()
    wait_for(selenium, By.CSS_SELECTOR, "input[type=submit]").click()
    #
    # selenium.find_element(By.ID, "select2-id_household-0-admin1_h_c-container").click()
    # time.sleep(1)
    # selenium.find_element(By.ID, "select2-id_household-0-admin2_h_c-container").click()
    # time.sleep(1)
    # selenium.find_element(By.ID, "select2-id_household-0-admin3_h_c-container").click()
    # find_by_css('fieldset.admin1_h_c .select2 .selection .select2-selection').click()

    # find_by_css("fieldset.admin1_h_c .select2")
    LOCATIONS = ["Автономна Республіка Крим", "Бахчисарайський", "Севастопільська"]

    find_by_css("fieldset.admin1_h_c .select2 .selection .select2-selection").click()
    find_by_css(".select2-search__field").send_keys(LOCATIONS[0])
    time.sleep(1)
    find_by_css(".select2-search__field").send_keys(Keys.ENTER)
    time.sleep(1)
    select = Select(selenium.find_element(By.CSS_SELECTOR, "select[name=household-0-admin1_h_c]"))
    assert select.first_selected_option.text == LOCATIONS[0]

    find_by_css("fieldset.admin2_h_c .select2 .selection .select2-selection").click()
    find_by_css(".select2-search__field").send_keys(LOCATIONS[1])
    time.sleep(1)
    find_by_css(".select2-search__field").send_keys(Keys.ENTER)
    time.sleep(1)
    select = Select(selenium.find_element(By.CSS_SELECTOR, "select[name=household-0-admin2_h_c]"))
    assert select.first_selected_option.text == LOCATIONS[1]

    find_by_css("fieldset.admin3_h_c .select2 .selection .select2-selection").click()
    find_by_css(".select2-search__field").send_keys(LOCATIONS[2])
    time.sleep(1)
    find_by_css(".select2-search__field").send_keys(Keys.ENTER)
    time.sleep(1)
    select = Select(selenium.find_element(By.CSS_SELECTOR, "select[name=household-0-admin3_h_c]"))
    assert select.first_selected_option.text == LOCATIONS[2]

    wait_for(selenium, By.CSS_SELECTOR, "input[type=submit]").click()

    #
    # find_by_css("fieldset.admin2_h_c .select2").click()
    # find_by_css('.select2-search__field').send_keys('Бахчисарайський')
    # time.sleep(1)
    # find_by_css('.select2-search__field').send_keys(Keys.ENTER)
    # time.sleep(2)
    #
    # find_by_css("fieldset.admin3_h_c .select2").click()
    # find_by_css('.select2-search__field').send_keys('Севастопільська')
    # time.sleep(1)
    # find_by_css('.select2-search__field').send_keys(Keys.ENTER)
    # time.sleep(1)

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

    find_by_css(f"a[href='{registration.get_absolute_url()}']").click()


#
# @pytest.mark.selenium
# def test_login_pwd_success(live_server, selenium, user):
#     from testutils.factories import CustomerFactory, SubscriptionFactory
#     customer = CustomerFactory(user=user)
#     SubscriptionFactory(customer=customer)
#
#     selenium.implicitly_wait(3)
#     selenium.get(f'{live_server.url}/')
#     dim = selenium.get_window_size()
#     selenium.set_window_size(1100, dim['height'])
#
#     wait_for(selenium, By.ID, 'id_login_email')
#     selenium.find_element(By.ID, 'toggler1').click()
#
#     selenium.find_element(By.NAME, 'auth-username').send_keys(user.username)
#     selenium.find_element(By.NAME, 'auth-password').send_keys(user._password)
#     selenium.find_element(By.ID, 'login-button-pwd').click()
#
#     wait_for(selenium, By.PARTIAL_LINK_TEXT, 'ADDRESSBOOK')
#     assert '/summary/' in selenium.current_url
#
#
# @pytest.mark.selenium
# def test_login_mail_link(live_server, selenium, user, mailoutbox):
#     from testutils.factories import CustomerFactory, SubscriptionFactory
#     customer = CustomerFactory(user=user)
#     SubscriptionFactory(customer=customer)
#
#     selenium.implicitly_wait(3)
#     selenium.get(f'{live_server.url}/')
#     dim = selenium.get_window_size()
#     selenium.set_window_size(1100, dim['height'])
#
#     wait_for(selenium, By.ID, 'id_login_email')
#     # selenium.find_element(By.ID, 'toggler1').click()
#
#     selenium.find_element(By.NAME, 'email').send_keys(user.email)
#     selenium.find_element(By.NAME, 'send-email').click()
#
#     wait_for_url(selenium, 'email/sent/')
#
#     assert len(mailoutbox) == 1
#
#
# @pytest.mark.selenium
# def test_login_2fa(live_server, selenium, user, monkeypatch):
#     from testutils.factories import CustomerFactory, SubscriptionFactory
#     customer = CustomerFactory(user=user)
#     SubscriptionFactory(customer=customer)
#     from django_otp.plugins.otp_totp.models import TOTPDevice
#     from two_factor.utils import totp_digits
#     device = TOTPDevice.objects.create(user=user, key='123',
#                                        tolerance=100, t0=0,
#                                        step=30, drift=0,
#                                        digits=totp_digits(),
#                                        name='default')
#
#     # monkeypatch.setattr('django_otp.match_token', lambda x, y: device)
#     monkeypatch.setattr('django_otp.forms.match_token', lambda x, y: device)
#
#     selenium.implicitly_wait(3)
#     selenium.get(f'{live_server.url}/')
#     dim = selenium.get_window_size()
#     selenium.set_window_size(1100, dim['height'])
#
#     wait_for(selenium, By.ID, 'id_login_email')
#     selenium.find_element(By.ID, 'toggler1').click()
#
#     selenium.find_element(By.NAME, 'auth-username').send_keys(user.username)
#     selenium.find_element(By.NAME, 'auth-password').send_keys(user._password)
#     selenium.find_element(By.ID, 'login-button-pwd').click()
#     selenium.find_element(By.NAME, 'token-otp_token').send_keys('123456')
#     selenium.find_element(By.ID, 'send-token-button').click()
#
#     wait_for_url(selenium, '/summary/')
#     assert '/summary/' in selenium.current_url
