# -*- coding: utf-8 -*-
__author__ = 'chinfeng'

import os
import sys
import threading
from .console import GumCmd
from .framework import Framework
from .configuration import LocalConfiguration

def _framework_loop(framework):
    extr = framework.__executor__
    while True:
        extr.wait_until_active()
        extr.step()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path',
                        dest='plugins_path', default='plugins',
                        help='plugins directory')
    parser.add_argument('-a', '--autostep', default=False,
                        dest='autostep', action='store_true',
                        help='auto push step')
    args = parser.parse_args()
    pt = os.path.abspath(args.plugins_path)
    autostep = args.autostep

    sys.path.append(pt)

    conf_pt = os.path.join(pt, '.configuration')
    if not os.path.isdir(conf_pt):
        os.mkdir(conf_pt)
    fmk = Framework(LocalConfiguration(conf_pt), pt)
    cmd = GumCmd(fmk, pt)
    if autostep:
        t = threading.Thread(target=_framework_loop, args=(fmk, ))
        t.setDaemon(True)
        t.start()
    try:
        cmd.cmdloop()
    finally:
        fmk.close()

if __name__ == '__main__':
    main()