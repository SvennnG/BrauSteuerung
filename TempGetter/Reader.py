import os

def tail(f, n, offset=0):
    if isinstance(f, str):
        stdin,stdout = os.popen2("tail -n %i %s" % (n+offset, f))
    else:
        stdin,stdout = os.popen2("tail -n %i %s" % (n+offset, f.name))
    stdin.close()
    lines = stdout.readlines(); stdout.close()
    if offset != 0:
        return lines[:-offset]
    return lines
    