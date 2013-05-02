
def inspect_args(*args):
    """Analyze arguments of function and print them using inspect

    #TODO: Need be set as a decorator. Kept it here for bookkeeping.
    """
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)

    print 'function name "%s"' % inspect.getframeinfo(frame)[2]
    for i in args:
        print "    %s = %s" % (i, values[i])


