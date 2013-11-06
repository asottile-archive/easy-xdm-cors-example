
import contextlib
import flask
import mock
import testify as T
import time
import werkzeug.exceptions

from util.auto_namedtuple import auto_namedtuple
from util.decorators import cached_property
from util.decorators import require_secure

class TestCachedProperty(T.TestCase):

    class Foo(object):
        @cached_property
        def foo(self):
            return "Foo" + str(time.time())

    def test_cached_property(self):
        instance = self.Foo()
        val = instance.foo
        val2 = instance.foo
        T.assert_is(val, val2)


    def test_unbound_cached_property(self):
        # Make sure we don't blow up when accessing the property unbound
        prop = self.Foo.foo
        T.assert_isinstance(prop, cached_property)

class TestRequireSecure(T.TestCase):
    """Tests the @require_secuer decorator."""

    def _get_fake_request(self, is_secure):
        return auto_namedtuple('MockRequest', is_secure=is_secure)

    def _get_callable_mock(self):
        mock_callable = mock.Mock()
        mock_callable.__name__ = 'foo'
        return mock_callable

    def test_ok_with_secure(self):
        """Tests that the method is called as usual with localhost."""
        mock_request = self._get_fake_request(True)
        arg = object()
        callable = self._get_callable_mock()

        with mock.patch.object(flask, 'request', mock_request):
            require_secure(callable)(arg)

        callable.assert_called_once_with(arg)

    def test_not_ok_with_not_secure(self):
        mock_request = self._get_fake_request(False)
        callable = self._get_callable_mock()

        with contextlib.nested(
            mock.patch.object(flask, 'request', mock_request),
            T.assert_raises(werkzeug.exceptions.Forbidden),
        ):
            require_secure(callable)()

    def test_non_decorator_secure(self):
        mock_request = self._get_fake_request(True)
        with mock.patch.object(flask, 'request', mock_request):
            require_secure()

    def test_non_decorator_with_not_secure(self):
       mock_request = self._get_fake_request(False)
       with contextlib.nested(
           mock.patch.object(flask, 'request', mock_request),
           T.assert_raises(werkzeug.exceptions.Forbidden),
       ):
           require_secure()

if __name__ == '__main__':
    T.run()
