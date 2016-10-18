#!/usr/bin/python
from __future__ import print_function
import argparse
import sys
import os

from wifi import Cell, Scheme
from wifi.utils import print_table, match as fuzzy_match
from wifi.exceptions import ConnectionError, InterfaceError

try:  # Python 2.x
    input = raw_input
except NameError:
    pass


def fuzzy_find_cell(interface, query):
    match_partial = lambda cell: fuzzy_match(query, cell.ssid)

    matches = Cell.where(interface, match_partial)

    num_unique_matches = len(set(cell.ssid for cell in matches))
    assert num_unique_matches > 0, "Couldn't find a network that matches '{}'".format(query)
    assert num_unique_matches < 2, "Found more than one network that matches '{}'".format(query)

    # Several cells of the same SSID
    if len(matches) > 1:
        matches.sort(key=lambda cell: cell.signal)

    return matches[0]


def find_cell(interface, query):
    cell = Cell.where(interface, lambda cell: cell.ssid.lower() == query.lower())

    try:
        cell = cell[0]
    except IndexError:
        cell = fuzzy_find_cell(interface, query)
    return cell


def get_scheme_params(interface, scheme, ssid=None):
    cell = find_cell(interface, ssid or scheme)
    passkey = None if not cell.encrypted else input('passkey> ')

    return interface, scheme, cell, passkey


def scan_command(args):
    print_table([[cell.signal, cell.ssid, 'protected' if cell.encrypted else 'unprotected'] for cell in Cell.all(args.interface)])


def list_command(args):
    for scheme in Scheme.for_file(args.file).all():
        print(scheme.name)


def show_command(args):
    scheme = Scheme.for_file(args.file).for_cell(*get_scheme_params(args.interface, args.scheme, args.ssid))
    print(scheme)


def add_command(args):
    scheme_class = Scheme.for_file(args.file)
    assert not scheme_class.find(args.interface, args.scheme), "That scheme has already been used"

    scheme = scheme_class.for_cell(*get_scheme_params(args.interface, args.scheme, args.ssid))
    scheme.save()


def connect_command(args):
    scheme_class = Scheme.for_file(args.file)
    if args.adhoc:
        # ensure that we have the adhoc utility scheme
        try:
            adhoc_scheme = scheme_class(args.interface, 'adhoc')
            adhoc_scheme.save()
        except AssertionError:
            pass
        except IOError:
            assert False, "Can't write on {0!r}, do you have required privileges?".format(args.file)

        scheme = scheme_class.for_cell(*get_scheme_params(args.interface, 'adhoc', args.scheme))
    else:
        scheme = scheme_class.find(args.interface, args.scheme)
        assert scheme, "Couldn't find a scheme named {0!r}, did you mean to use -a?".format(args.scheme)

    try:
        scheme.activate()
    except ConnectionError:
        assert False, "Failed to connect to %s." % scheme.name


def autoconnect_command(args):
    ssids = [cell.ssid for cell in Cell.all(args.interface)]

    for scheme in Scheme.all():
        # TODO: make it easier to get the SSID off of a scheme.
        ssid = scheme.options.get('wpa-ssid', scheme.options.get('wireless-essid'))
        if ssid in ssids:
            sys.stderr.write('Connecting to "%s".\n' % ssid)
            try:
                scheme.activate()
            except ConnectionError:
                assert False, "Failed to connect to %s." % scheme.name
            break
    else:
        assert False, "Couldn't find any schemes that are currently available."


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--interface',
                        default='wlan0',
                        help="Specifies which interface to use (wlan0, eth0, etc.)")
    parser.add_argument('-f',
                        '--file',
                        default='/etc/network/interfaces',
                        help="Specifies which file for scheme storage.")

    subparsers = parser.add_subparsers(title='commands')

    parser_scan = subparsers.add_parser('scan', help="Shows a list of available networks.")
    parser_scan.set_defaults(func=scan_command)

    parser_list = subparsers.add_parser('list', help="Shows a list of networks already configured.")
    parser_list.set_defaults(func=list_command)

    scheme_help = ("A memorable nickname for a wireless network."
                   "  If SSID is not provided, the network will be guessed using SCHEME.")
    ssid_help = ("The SSID for the network to which you wish to connect."
                 "  This is fuzzy matched, so you don't have to be precise.")

    parser_show = subparsers.add_parser('config',
                                        help="Prints the configuration to connect to a new network.")
    parser_show.add_argument('scheme', help=scheme_help, metavar='SCHEME')
    parser_show.add_argument('ssid', nargs='?', help=ssid_help, metavar='SSID')
    parser_show.set_defaults(func=show_command)

    parser_add = subparsers.add_parser('add',
                                       help="Adds the configuration to connect to a new network.")
    parser_add.add_argument('scheme', help=scheme_help, metavar='SCHEME')
    parser_add.add_argument('ssid', nargs='?', help=ssid_help, metavar='SSID')
    parser_add.set_defaults(func=add_command)

    parser_connect = subparsers.add_parser('connect',
                                           help="Connects to the network corresponding to SCHEME")
    parser_connect.add_argument('scheme',
                                help="The nickname of the network to which you wish to connect.",
                                metavar='SCHEME')
    parser_connect.add_argument('-a',
                                '--ad-hoc',
                                dest='adhoc',
                                action="store_true",
                                help="Connect to a network without storing it in the config file")
    parser_connect.set_defaults(func=connect_command)

    # TODO: how to specify the correct interfaces file to work off of.
    parser_connect.get_options = lambda: [scheme.name for scheme in Scheme.all()]

    parser_autoconnect = subparsers.add_parser(
        'autoconnect',
        help="Searches for saved schemes that are currently"
             " available and connects to the first one it finds."
    )
    parser_autoconnect.set_defaults(func=autoconnect_command)

    return parser, subparsers


def autocomplete(position, wordlist, subparsers):
    if position == 1:
        ret = subparsers.choices.keys()
    else:
        try:
            prev = wordlist[position - 1]
            ret = subparsers.choices[prev].get_options()
        except (IndexError, KeyError, AttributeError):
            ret = []

    print(' '.join(ret))


def main():
    parser, subparsers = arg_parser()
    argv = sys.argv[1:]
    args = parser.parse_args(argv)

    try:
        if 'WIFI_AUTOCOMPLETE' in os.environ:
            autocomplete(int(os.environ['COMP_CWORD']),
                         os.environ['COMP_WORDS'].split(), subparsers)
        else:
            command = getattr(args, 'func', scan_command)
            command(args)
    except (AssertionError, InterfaceError) as e:
        sys.stderr.write("Error: ")
        sys.exit(e)
