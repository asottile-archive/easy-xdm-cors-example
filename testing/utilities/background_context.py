
import contextlib
import subprocess
import threading

class BackgroundContext(object):

    def background_action(self):
        raise NotImplementedError

    def teardown(self):
        raise NotImplementedError

    def start(self):
        self.thread = threading.Thread(target=self.background_action)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.teardown()
        self.thread.join()

    @classmethod
    @contextlib.contextmanager
    def in_context(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        instance.start()
        try:
            yield instance
        finally:
            instance.stop()

class SubprocessBackgroundContext(BackgroundContext):

    command = None

    def start(self):
        self.process = subprocess.Popen(self.command)

    def stop(self):
        # TODO(asottile): should use some sort of timeout here
        self.process.terminate()
        self.process.wait()
