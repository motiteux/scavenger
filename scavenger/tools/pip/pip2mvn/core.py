#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on Oct 9, 2012

"""Spawning downloads to many workers"""

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
            for l in lib:
                print "Trying to install %s"%l
                run("pip install %s"%l)
            return time.time() - start
        else:
            syntax()
            exit()
    except:
        print "Unhandled exception"
        exit()


def parallel_download(lib = None):
    try:
        if lib:
            print "spawning using gevent"
            jobs = [gevent.spawn(pip.util.call_subprocess, ["pip","install",l]) \
                                                      for l in lib]
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
