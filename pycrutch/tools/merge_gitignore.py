#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This module merges existing .gitignore files from several location in
# a git repository into one root .gitignore file
#
# Created on Jan 24, 2013
#
# @author:  Marc-Olivier Titeux
# Nimble Rock

from __future__ import print_function

'''
Merge several .gitignore files from a git repository in one and only file to 
rule them all.
'''

__authors__ = [  # alphabetical order by last name, please
                '"Marc-Olivier Titeux" <marcolivier.titeux@gmail.com>',
                ]

import os 
import argparse
import logging
from functools import partial


logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S')

def merge_gitignore(to_path, output):
    """ :to_path str path to the git repository"""
    ignore_list = set()

    for root, dirs, files in os.walk(to_path):
        for name_f in files:
            if name_f == ".gitignore":
                logging.debug("Found .gitignore in {0}".format(root))
                if root is not to_path:
                    path_ignore = partial(os.path.join, os.path.relpath(root, to_path))
                    ignore_list |= set(map(path_ignore, 
                            [el.lstrip('//') for el in 
                            open(os.path.join(root, name_f)).read().splitlines()]))
                else:
                    ignore_list |= set(open(os.path.join(root, name_f)).read().splitlines())
                if root is not to_path:
                    os.remove(os.path.join(root, name_f))

    with open(os.path.join(to_path, output), 'w') as file_w:
        print_filew = partial(print, file=file_w)
        map(print_filew, sorted(ignore_list))


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
                description=("This Python module provides a way to merge "
                        ".gitignore files in a git repository."),
                         prog='MergeIgnores',
                         epilog="contact: marcolivier.titeux@gmail.com")
    parser.add_argument('to_path', metavar='path to git repos ', type=str)
    parser.add_argument('--output', metavar='Output name of the merged file', 
                        type=str,
                        default=".gitignore")

    try:
        argps = parser.parse_args()
        to_path = argps.to_path
        output = argps.output
    except IOError, msg:
        parser.error(str(msg))

    logging.info("Merging .gitignore files in {0}".format(to_path))
    merge_gitignore(to_path, os.path.join(to_path, output))


if __name__ == "__main__":
    main()
