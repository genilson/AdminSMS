#!/usr/bin/env python
# coding: utf-8

'''
.. moduleauthor:: Genilson Israel da Silva <genilsonisrael@gmail.com>

:Platform: \*nix

:Synopsis: adminssms - creates the daemon implemented in :class:`Daemon`
    and listens to registered and authorized phone SMS notifications, executes
    commands in the SMS message and sends a reply with:
        - errors that might occur or
        - output of the command
    If the output is more than 160 characters long, sends default message
    instead

'''

from sms.smsdaemon import SMSD
from argparse import ArgumentParser
import sys

if __name__ == '__main__':
    # Setting up the log files and the file that will keep track of the pid
    daemon = SMSD('/tmp/smsd.pid',
                  stdout='/var/log/smsd_log',
                  stderr='/var/log/smsd_err_log')
    parser = ArgumentParser()
    parser.add_argument('arg', help='[ start | stop | status ]')
    args = parser.parse_args()

    if args.arg == 'start':
        daemon.start()
    elif args.arg == 'stop':
        daemon.stop()
    elif args.arg == 'status':
        daemon.status()
    else:
        parser.print_help()
        sys.exit(2)
    sys.exit(0)
