#/bin/env python

"""Monitor time using a context

with FileStatus(self.file_status_path) as file_status, Timer() as timer:
    ... Doing smthg

    print timer.duration_in_seconds()

"""

import time


class Timer(object):
    """Context Manager to track elapsed time in computation. This could allow
    to restart operation by changing __enter__, or using memoization.
    """
    def __init__(self):
        self.__start = 0
        self.__finish = 0

    def __enter__(self):
        self.__start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        # Error handling here
        self.__finish = time.time()
        return isinstance(value, KeyboardInterrupt)

    def current_duration(self):
        """Instantaneous time."""
        return time.time() - self.__start

    def duration_in_seconds(self):
        """Final duration."""
        return self.__finish - self.__start
