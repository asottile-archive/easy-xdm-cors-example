import contextlib
import os
from selenium.webdriver.remote import webdriver
from selenium.webdriver import DesiredCapabilities
import simplejson
import testify as T


def get_command_executor_url(host, path, port=80, user=None, passwd=None):
    """Creates a url for connecting to a selenium webdriver server."""
    if passwd and not user:
        raise ValueError("Can't build a valid url containing an access key without a user")

    url = 'http://'

    if user:
        if passwd:
            url += '{0}:{1}@'.format(user, passwd)
        else:
            url += '{0}@'.format(user)

    return url + '{host}:{port}/{path}'.format(host=host, port=port, path=path)

@contextlib.contextmanager
def remote_web_driver(desired_capabilities, implicit_wait=15):
    command_executor_url = get_command_executor_url(
        host=os.environ.get('SELENIUM_HOST', 'localhost'),
        path=os.environ.get('SELENIUM_PATH', 'wd/hub'),
        port=int(os.environ.get('SELENIUM_PORT', '4444')),
        user=os.environ.get('SELENIUM_USER', 'nobody'),
        passwd=os.environ.get('SELENIUM_PASSWORD', 'password')
    )

    driver = webdriver.WebDriver(
        desired_capabilities=desired_capabilities,
        command_executor=command_executor_url,
    )

    driver.implicitly_wait(implicit_wait)

    try:
        yield driver
    finally:
        driver.quit()

@T.suite('selenium')
class IntegrationTestBrowsers(T.TestCase):

    SENSITIVE_INFO = {
        'first_name': 'Anthony',
        'last_name': 'Sottile',
        'phone': '555-555-5555',
        'email': 'herp.derp@example.com',
    }

    def _test_cors(self, driver):
        driver.get('http://localhost:5000/')
        driver.find_element_by_css_selector('.first-name').send_keys(self.SENSITIVE_INFO['first_name'])
        driver.find_element_by_css_selector('.last-name').send_keys(self.SENSITIVE_INFO['last_name'])
        driver.find_element_by_css_selector('.email').send_keys(self.SENSITIVE_INFO['email'])
        driver.find_element_by_css_selector('.phone').send_keys(self.SENSITIVE_INFO['phone'])
        driver.find_element_by_css_selector('.cors-now').click()
        T.assert_equal(
            {
                'original_request': self.SENSITIVE_INFO,
                'success': True,
            },
            simplejson.loads(
                driver.find_element_by_css_selector('.cors-status div').text
            )
        )

    def test_firefox(self):
        with remote_web_driver(DesiredCapabilities.FIREFOX) as driver:
            self._test_cors(driver)

    def test_chrome(self):
        with remote_web_driver(DesiredCapabilities.CHROME) as driver:
            self._test_cors(driver)
