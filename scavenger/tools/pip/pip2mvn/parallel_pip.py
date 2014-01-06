#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 31/05/2013

"""Use pip in parallel
https://gist.github.com/kracekumar/1971720

System dependency: libevent-devel

WARNING: Does not work with a requirements file (yet)

"""

__all__ = []


from gevent import monkey
monkey.patch_all()

import gevent
import time
from envoy import run
from sys import exit, argv
import subprocess
import pip


def syntax():
    print "Usage:python core.py normal|parallel [libraries]"


def normal_download(lib = None):
    try:
        if lib:
            start = time.time()
            print "normal download started"
            with open(lib[0], 'r') as req_file:
                req_list = req_file.readlines()
                for req in req_list:
                    if not req.startswith('#'):
                        print "Trying to install %s"%req
                        run("pip install %s"%req)
            return time.time() - start
        else:
            syntax()
            exit()
    except:
        print "Unhandled exception"
        exit()


def parallel_download(lib=None):
    try:
        if lib:
            print "spawning using gevent"
            with open(lib[0], 'r') as req_file:
                req_list = req_file.readlines()

                jobs = [gevent.spawn(pip.util.call_subprocess, ["pip","install",req]) \
                                                      for req in req_list if not req.startswith('#')]
                start = time.time()
                print "joined all gevent, d/l started"
                gevent.joinall(jobs)
                for job in jobs:
                    print job.value
                return time.time() - start
        else:
            syntax()
            exit()
    except Exception, e:
        print "unhandled exception", e
        exit()

if __name__ == "__main__":
    if argv[1] == 'parallel':
        print(parallel_download(argv[2:])," seconds for parallel d/l")
    elif argv[1] == 'normal':
        print(normal_download(argv[2:]), "seconds for normal d/l")
    else:
        syntax()
        exit()