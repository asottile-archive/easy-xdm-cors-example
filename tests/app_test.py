
from __future__ import absolute_import

import flask

from testing.assertions.response import assert_no_response_errors
from testing.base_classes.easy_xdm_cors_example_server_test_case import EasyXDMCORSExampleServerTestCase

class TestIndex(EasyXDMCORSExampleServerTestCase):

    def test_index_loads(self):
        response = self.client.get(flask.url_for('index'))
        assert_no_response_errors(response)

class TestCatchall(EasyXDMCORSExampleServerTestCase):

    def test_cors_index(self):
        response = self.client.get('/cors/index.html')
        assert_no_response_errors(response)

    def test_easy_xdm_js(self):
        response = self.client.get('/easyXDM.debug.js')
        assert_no_response_errors(response)
