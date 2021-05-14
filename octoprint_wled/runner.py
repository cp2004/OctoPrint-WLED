"""
Handles all calling the API of WLED in a non-blocking way (most of the time)
"""
import logging
import queue
from typing import Any, Optional

import octoprint_wled
from octoprint_wled.constants import KILL_MESSAGE
from octoprint_wled.util import start_thread
from octoprint_wled.wled import WLEDError

# Effects are put into the queue like this:
# {"target": WLED, "args": (tuple of args), "kwargs": {dict of kwargs}}


class WLEDRunner:
    def __init__(self, plugin):
        self.plugin = plugin  # type: octoprint_wled.WLEDPlugin

        self.queue = queue.Queue()
        self._logger = logging.getLogger("octoprint.plugins.wled.runner")

        self.runner_thread = start_thread(self.runner_thread)

    def runner_thread(self):
        while True:
            message = self.queue.get(block=True)
            if message == KILL_MESSAGE:
                # We are done, return, goodbye, have a nice day
                return

            # All other things should be WLED messages
            try:
                self._call_wled(**message)
            except Exception as e:
                # Don't bother to properly do something about errors here, just log and try again
                # In theory this shouldn't happen, if it does then I should fix it...
                self._logger.exception(e)
                continue

    def kill(self):
        self.queue.put(KILL_MESSAGE)
        self.runner_thread.join(5)

    def _call_wled(self, target, args=(), kwargs=None, suppress_exceptions=True) -> Any:
        def log_caller():
            self._logger.debug(f"Target: {target.__qualname__}")
            self._logger.debug(f"Args: {args}")
            self._logger.debug(f"Kwargs: {kwargs}")

        if kwargs is None:
            kwargs = {}

        if not callable(target):
            raise RuntimeError("Can't call an uncallable thing, you broke it")

        try:
            response = target(*args, **kwargs)
        except WLEDError as e:
            # noinspection PyProtectedMember
            if suppress_exceptions:
                self._logger.error(f"Can't connect to WLED, {repr(e)}")
                log_caller()
                return
            else:
                raise
        except Exception as e:
            if suppress_exceptions:
                # Yeah that was bad naming. It means don't raise exceptions
                # any higher up, just log and move on with life
                self._logger.exception(f"Unknown error calling WLED: \n{e}")
                log_caller()
                return
            else:
                raise

        return response

    def wled_call(
        self,
        target,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        block: bool = False,
        suppress_exceptions: bool = True,
    ) -> Any:
        if kwargs is None:
            kwargs = {}
        if not block:
            # Call WLED asynchronously, no response
            message = {
                "target": target,
                "args": args,
                "kwargs": kwargs,
            }
            self.queue.put(message)
        else:
            # Call synchronously, if the response is needed
            return self._call_wled(target, args, kwargs, suppress_exceptions)
