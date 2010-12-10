#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess


def try_connect(host):
    parts = host.split(':', 3)
    command = ['sshpass', '-p', "'%s'" % parts[2].strip(), 'ssh', parts[0], \
        '-p', parts[1], '-o', 'PubkeyAuthentication=no', \
        '-o', 'ConnectTimeout=10', \
        '-o', 'StrictHostKeyChecking=no', '"exit 0"']

    try:
        returncode = subprocess.check_call(command, \
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        code = '[%s]' % e.returncode
        return '%s %s:%s' % (code.ljust(5), parts[0], parts[1])
    except subprocess.CalledProcessError, e:
        code = '[%s]' % e.returncode
        return '%s %s:%s' % (code.ljust(5), parts[0], parts[1])


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
