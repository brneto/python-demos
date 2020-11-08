#!/usr/bin/env python

from stub_manager import run


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 3:
        run(port=int(argv[1]), consumer=str(argv[2]))
    elif len(argv) == 2:
        arg = argv[1]
        try:
            int_arg = int(arg)
            run(port=int_arg)
        except ValueError:
            run(consumer=arg)
    else:
        run()
