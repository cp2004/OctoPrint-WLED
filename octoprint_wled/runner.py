"""
Handles all calling the API of WLED in a non-blocking way (most of the time)
"""
import logging
import queue
import threading
from typing import Any, Optional

import octoprint_wled
from octoprint_wled.constants import KILL_MESSAGE
from octoprint_wled.wled import WLEDError

# Effects are put into the queue like this:
# {"target": WLED, "args": (tuple of args), "kwargs": {dict of kwargs}}


class WLEDRunner:
    def __init__(self, plugin):
        self.plugin = plugin  # type: octoprint_wled.WLEDPlugin

        self.queue = queue.Queue()
        self._logger = logging.getLogger("octoprint.plugins.wled.runner")

        self.runner = threading.Thread(target=self.runner_thread)
        self.runner.daemon = True
        self.runner.start()

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

    def _call_wled(self, target, args=(), kwargs=None) -> Any:
        if kwargs is None:
            kwargs = {}

        if not callable(target):
            raise RuntimeError("Can't call an uncallable thing, you broke it")

        try:
            response = target(*args, **kwargs)
        except WLEDError as e:
            # noinspection PyProtectedMember
            self._logger.debug(f"Can't connect to WLED, {repr(e)}")
            return
        except Exception as e:
            self._logger.exception(e)
            return

        return response

    def wled_call(
        self,
        target,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        block: bool = False,
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
            return self._call_wled(target, args, kwargs)
