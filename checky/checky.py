#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess


def try_connect(host):
    parts = host.split(':', 3)
    command = ['sshpass', '-p', "'%s'" % parts[2].strip(), 'ssh', parts[0], \
        '-p', parts[1], '"exit 0"']
#    for c in command:
#        sys.stdout.write(c + ' ')
#    sys.stdout.flush()
    try:
        return subprocess.check_call(command, \
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError, e:
        if e.returncode <= 5:
            return 'OK: %s:%s' % (parts[0], parts[1])
        else:
            return 'Error: Can\'t connect to %s:%s' % (parts[0], parts[1])


def main():
    if len(sys.argv) > 1:
        f = open(sys.argv[1], 'r')
        for line in f:
            print try_connect(line)
        f.close()
    else:
        print 'Usage: checky <host_list_file>'


if __name__ == '__main__':
    main()
