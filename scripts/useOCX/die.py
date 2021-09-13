import sys
import traceback


def Die(Msg):
    print(sys.stderr)
    print(sys.stderr)

    traceback.print_stack()
    s = ""
    for i in range(0, len(sys.argv)):
        if i > 0:
            s += " "
        s += sys.argv[i]
    print(s, sys.stderr)
    print(Msg, "**ERROR**", file=sys.stderr)
    print(sys.stderr)
    print(sys.stderr)
    sys.exit(1)

def Warning(Msg):
    print(sys.stderr)
    print(sys.argv, sys.stderr)
    print(Msg, "**WARNING**", sys.stderr)

