#!/usr/bin/env python
# -*- coding: utf-8 -*-


# @author: Unknown
# src: http://pastebin.com/Lu4EtNuD

"""
Pipe arguments almost like REPL
"""

def PipeLine(*args, **kwargs):
    """
   Given an arbitrary number of functions we create a pipeline where the output
   is piped between functions. you can also specify a tuple of arguments that
   should be passed to functions in the pipeline. The first arg is always the
   output of the previous function.
   """
    def wrapper(*data):
        if len(args) == 1:
            if args[-1].__name__ in kwargs:
                otherArgs = data + kwargs[args[-1].__name__]
                return args[-1](*otherArgs)
            else:
                return args[-1](*data)
        else:
            if args[-1].__name__ in kwargs:
                otherArgs = kwargs[args[-1].__name__]
                del kwargs[args[-1].__name__]
                return args[-1](PipeLine(*args[:-1], **kwargs)(*data), *otherArgs)
            else:
                return args[-1](PipeLine(*args[:-1], **kwargs)(*data))
    return wrapper
 
 
def testPipelineWithArgs():
    """
   Test all the major functionality:
   multiple functions, initial arguments
   per function arguments stored in kwargs
   """
    def add1(input_):
        return input_ + 1
 
    def subX(input_, x):
        return input_ - x
 
    def stringify(input_):
        return str(input_)
 
    pipeline = PipeLine(
        add1,
        subX,
        stringify,
        subX=(2,),
        )
    print pipeline(10)
