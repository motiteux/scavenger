# -*- coding: utf-8 -*-

__author__ = 'marco'


class FileStatus(file):
    """Context Manager to track files that report timing, convergence and
    issues in Prometheus operations.

    """
    def __init__(self, f_stream):
        super(FileStatus, self).__init__(f_stream, 'a+')
        self.file = f_stream

    def __enter__(self):
        open(self.file, 'a+')
        return self

    def __exit__(self, type, value, traceback):
        #TODO: Error handling here
        return isinstance(value, KeyboardInterrupt)
