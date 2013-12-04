#/bin/env python

"""Replace trace function by one that displays all calls, 
with some details"""

def trace_func(frame, event, arg):
    print 'Context: ', frame.f_code.co_name, \
        '\tFile:', frame.f_code.co_filename, \
        '\tLine:', frame.f_lineno, \
        '\tEvent:', event
    return trace_func

sys.settrace(trace_func)
