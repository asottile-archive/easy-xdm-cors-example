
import testify as T

from testing.base_classes.flask_test_case import FlaskTestCase
from easy_xdm_cors_example.app import app

@T.suite('integration')
class EasyXDMCORSExampleServerTestCase(FlaskTestCase):
    __test__ = False

    FLASK_APPLICATION = app
