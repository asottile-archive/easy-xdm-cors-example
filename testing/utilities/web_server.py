
from testing.utilities.background_context import SubprocessBackgroundContext

class WebServer(SubprocessBackgroundContext):

    def __init__(self, is_ssl):
        super(WebServer, self).__init__()
        self.command = [
            'python', '-m', 'easy_xdm_cors_example.app',
        ]
        if is_ssl:
            self.command.append('--ssl')

    @property
    def extended_env(self):
        env = super(WebServer, self).extended_env
        env['PYTHONPATH'] = '.'
        return env
