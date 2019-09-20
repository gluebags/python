#!/usr/bin/env python3.5
# mass ssh to /group0 or /group1
import sys
import os
import argparse
from subprocess import Popen, PIPE

def gethosts(servers):
    with open(servers, 'r') as f:
        zug = [ l.strip('\n') for l in f.read().split(' ') ]
        return ' '.join(zug)

def lookatlogs(lookingfor, servers):
    print("Executing {0} on {1}\n".format(lookingfor, servers))
    _pssh = "pssh -H \'{0}\' -p 30 -i \"{1}\"".format(servers, lookingfor)
    line = Popen([ _pssh ], stdout=PIPE, stderr=PIPE, shell=True)
    output, error = line.communicate()

    lines = ""
    fails = ""
    hname = ""

    for o in output.decode("utf-8").split('\n'):
        if '[FAILURE]' in o:
            fails += '{0}\n'.format(o.strip())
            hname = '{0}'.format(o.split()[3])
        elif '[SUCCESS]' in o:
            hname = '{0}'.format(o.split()[-1])
        elif o:
            lines += '{0}: {1}\n'.format(hname, o.strip())
    if lines == "":
        print("No matches using {0} found on {1}\n".format(
            lookingfor,
            servers)
            )
        #Exits out without thowing an exception
        os._exit(1)

    return lines, fails

def sortlogs(logs):
    logs_to_sort = [x for x in logs.split("\n") if x]
    sorted_logs = sorted(
        logs_to_sort,
        key=lambda x: ( x.split()[2], x.split()[3] ))
    return '\n'.join(sorted_logs)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Mass ssh')
    parser.add_argument(
        '-c',
        '--command',
        type=str,
        help='Command to send to hosts',
        required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-filters',
        help='Filter Hosts',
        action='store_true')
    group.add_argument(
        '-relays',
        help='Relay Hosts',
        action='store_true')
    group.add_argument(
        '-all',
        help='Filter and Relay Hosts',
        action='store_true')
    group.add_argument(
        '-hosts',
        help='Specific hosts provided',
        nargs='*')
    parser.add_argument(
        '-printfail',
        help='Will output failures',
        action ='store_true')
    parser.add_argument(
        '-sortlogs',
        help='Output logs in chronological',
        action = 'store_true')

    if len(sys.argv) == 1:
            sys.exit(parser.print_help())

    args =  parser.parse_args()

    if args.filters:
        connecting_to = gethosts('/group1')

    if args.relays:
        connecting_to = gethosts('/group0')

    if args.all:
        connecting_to = (gethosts('/group1') + " " +
            gethosts('/group0'))

    if args.hosts:
        connecting_to = " ".join(args.hosts)

    try:
        hits, miss =  lookatlogs(args.command, connecting_to)

        if not args.sortlogs:
            print(hits)
        else:
            print(sortlogs(hits))

        if args.printfail:
            print("Didn't find hits on below")
            print(miss)

    except KeyboardInterrupt:
        sys.exit("Aborting due to keyboard Interrupt")

    except:
        print(sys.exc_info())
        sys.exit("Something has gone terribly wrong")
