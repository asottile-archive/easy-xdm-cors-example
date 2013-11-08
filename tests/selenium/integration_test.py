import contextlib
import functools
import os
from selenium.webdriver.remote import webdriver
from selenium.webdriver import DesiredCapabilities
import simplejson
import testify as T
import types

from easy_xdm_cors_example.app import HTTP_PORT
from testing.utilities.proxy import ProxyServer
from testing.utilities.web_server import WebServer

PROXY_URL = 'localhost:8080'

IE_VERSION_TO_OS = {
    '8': 'Windows XP',
    '9': 'Windows 7',
    '10': 'Windows 7',
    '11': 'Windows 8.1',
}

def get_ie_capabilities(version):
    capabilities = DesiredCapabilities.INTERNETEXPLORER.copy()
    capabilities.update({
        'version': version,
        'platform': IE_VERSION_TO_OS[version],
    })
    return capabilities


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

def proxy_capabilities(desired_capabilities, proxy_url):
    desired_capabilities['proxy'] = {
        "httpProxy": proxy_url,
        "ftpProxy": proxy_url,
        "sslProxy": proxy_url,
        "noProxy": None,
        "proxyType": "MANUAL",
        "class": "org.openqa.selenium.Proxy",
        "autodetect": False,
    }

@contextlib.contextmanager
def remote_webdriver(desired_capabilities, implicit_wait=15):
    command_executor_url = get_command_executor_url(
        host=os.environ.get('SELENIUM_HOST', 'localhost'),
        path=os.environ.get('SELENIUM_PATH', 'wd/hub'),
        port=int(os.environ.get('SELENIUM_PORT', '4444')),
        user=os.environ.get('SELENIUM_USER', 'nobody'),
        passwd=os.environ.get('SELENIUM_PASSWORD', 'password')
    )

    proxy_capabilities(desired_capabilities, PROXY_URL)

    driver = webdriver.WebDriver(
        desired_capabilities=desired_capabilities,
        command_executor=command_executor_url,
    )

    driver.implicitly_wait(implicit_wait)

    try:
        yield driver
    finally:
        driver.quit()

@contextlib.contextmanager
def web_servers_running():
    with contextlib.nested(
        WebServer.in_context(True),
        WebServer.in_context(False),
    ):
        yield

def multiple_suites(*suites):
    def _multiple_suites(func):
        for suite in suites:
            func = T.suite(suite)(func)
        return func
    return _multiple_suites

@T.suite('selenium')
class IntegrationTestBrowsers(T.TestCase):

    SENSITIVE_INFO = {
        'first_name': 'Anthony',
        'last_name': 'Sottile',
        'phone': '555-555-5555',
        'email': 'herp.derp@example.com',
    }

    BROWSER_SUITES = [
        DesiredCapabilities.FIREFOX.copy(),
        DesiredCapabilities.CHROME.copy(),
        get_ie_capabilities('8'),
        get_ie_capabilities('9'),
        get_ie_capabilities('10'),
        get_ie_capabilities('11'),
    ]

    @T.class_setup_teardown
    def web_servers(self):
        with web_servers_running():
            yield

    def _test_cors(self, capabilities):
        with remote_webdriver(capabilities) as driver:
            with ProxyServer.in_context() as proxy:
                driver.get('http://localhost:{0}/'.format(HTTP_PORT))
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

                # Make sure none of our sensitive values were leaked
                for value in self.SENSITIVE_INFO.values():
                    T.assert_not_in(value, proxy.sniffable_content)
                T.assert_in('jquery', proxy.sniffable_content)

    def __init__(self, *args, **kwargs):
        super(IntegrationTestBrowsers, self).__init__(*args, **kwargs)

        # Add a test for each of our tests
        for capabilities in self.BROWSER_SUITES:
            browser = capabilities['browserName'].replace(' ', '-')
            version = capabilities.get('version', 'ANY').replace(' ', '-')
            platform = capabilities.get('platform', 'ANY').replace(' ', '-')
            test_name = 'test_{0}_{1}_{2}'.format(
                browser, version, platform,
            )
            test = functools.partial(self._test_cors.im_func, capabilities=capabilities)
            test.__name__ = test_name
            # Give it suites for the browser
            test = multiple_suites(
                browser,
                '_'.join([browser, version]),
                '_'.join([browser, version, platform]),
            )(test)
            test = types.MethodType(test, self, type(self))
            setattr(self, test_name, test)
