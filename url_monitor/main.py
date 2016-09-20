#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import json
import logging
import os
import sys
import textwrap

import requests

import commons
import configuration
import zbxsend as event
from zbxsend import Metric

from url_monitor import authors as authorsmacro
from url_monitor import authors as emailsmacro
from url_monitor import project as projectmacro
from url_monitor import description as descriptionmacro

__doc__ = """Program entry point"""


def return_epilog():
    """ Formats the eplig footer generated by help """
    author_strings = []
    for name, email in zip(authorsmacro, emailsmacro):
        author_strings.append('Author: {0} <{1}>'.format(name, email))
    return (
        "{project}\n"
        "{footerline}\n"
        "{authors}"
    ).format(
        footerline=str('-' * 72),
        project=projectmacro,
        authors='\n'.join(author_strings)
        )


def check(testSet, configinstance, logger):
    """
    Perform the checks when called upon by argparse in main()

    :param testSet:
    :param configinstance:
    :param logger:
    :return:
    """

    constant_zabbix_port = 10051

    config = configinstance.load()
    webinstance = commons.WebCaller(logger)

    try:  # Grab local requests timeout else defer to main setting
        tmout = int(testSet['data']['request_timeout'])  # in seconds
    except:
        tmout = int(config['config']['request_timeout'])

    # SSL validation
    try:  # Use SSL local security (if available)
        globaldefer = False  # Disable global security lookup
        vfyssl = commons.string2bool(testSet['data']['request_verify_ssl'])
    except:
        globaldefer = True

    try:  # Use SSL global local security or default to SECURE
        if globaldefer:
            vfyssl = commons.string2bool(
                config['config']['request_verify_ssl'])
    except:
        vfyssl = True

    # Make a request and check a resource
    try:
        uri = testSet['data']['uri']
    except KeyError as err:
        # We're missing the uri aren't we?
        error = ("Error: Missing {err} under testSet item {item}, "
                 "check cannot run.").format(err=err, item=testSet['key'])
        raise Exception("KeyError: " + str(err) + str(error))
    try:
        response = webinstance.run(config, uri, verify=vfyssl, expected_http_status=str(
            testSet['data']['ok_http_code']), identity_provider=testSet['data']['identity_provider'], timeout=tmout)
    except KeyError, err:
        # We're missing ok code arent we?
        error =  """KeyError Missing {err}  under testSet item {key} If you don't know `ok_http_code: any` will cover most services.""".format(
            err=err, key=str(testSet['key']))
        logging.exception(error)
        return 1
    except requests.exceptions.RequestException as e:
        logging.exception(
            "requests.exceptions.RequestException: {e}".format(e=e))
        return 1
    except commons.AuthException as err:
        logging.exception("Error logging into the ")
        return 1

    # This is the host defined in your metric.
    # This matches the name of your host in zabbix.
    zabbix_metric_host = config['config']['zabbix']['host']

    metrics = []
    # For each testElement do our path check.
    for element in testSet['data']['testElements']:
        try:
            datatypes = element['datatype'].split(',')
        except KeyError as err:
            logging.error("Error: Missing " + str(err) +
                          " in config under testSet: testElements, check cannot run.")
            logging.error(
                "Most elements are dynamically generated but this one is required.")
            logging.error(
                "You can generate 1 or a comma seperated list of datatypes")
            return 1
        # We need to make a metric for each explicit data type
        # (string,int,count)
        for datatype in datatypes:
            try:
                path = commons.omnipath(response.content, testSet[
                    'data']['response_type'], element)
            except KeyError as err:
                # We're missing one of these two keys aren't we?
                logging.exception(
                    "KeyError {err} missing in config under testElement, check cannot run. Must be response_type json or xml".format(err=err))
                return 1
            # Append to the element things like response, statuscode,
            # and the request url, I'd like to monitor status codes but don't
            # know what that'll take.

            element['datatype'] = datatype
            element['request_response'] = path
            element['request_statuscode'] = response.status_code
            element['uri'] = uri

            try:
                element['key']
            except KeyError as err:
                logging.error("Error: Missing " + str(err) +
                              " in config under testSet: testElements, check cannot run.")
                logging.error(
                    "Most elements are dynamically generated but this one is required.")
                return 1
            logging.debug(str(element['key']) + ": " +
                          str(element['request_response']))

            # Applies a key format from the configuration file, allowing custom zabbix keys
            # for your items reporting to zabbix. Any element in testSet can be substituted,
            #  the {uri} and Pdatatype} are also made available.
            metrickey = config['config']['zabbix'][
                'item_key_format'].format(**element)

            metrics.append(Metric(zabbix_metric_host,
                                  metrickey,
                                  element['request_response']))

    z_host, z_port = commons.get_hostport_tuple(
        constant_zabbix_port, config['config']['zabbix']['server'])

    timeout = float(config['config']['zabbix']['send_timeout'])
    # Send metrics to zabbix
    logging.debug(
        "Prepping transmit metrics to zabbix... {metrics}".format(metrics=metrics))
    logging.info("Transmit metrics to Zabbix @ {zbxhost}:{zbxport}".format(
        zbxhost=z_host, zbxport=z_port))
    event.send_to_zabbix(metrics=metrics, zabbix_host=z_host,
                         zabbix_port=z_port, timeout=timeout, logger=logger)
    return 0


def discover(args, configinstance, logger):
    """
    Perform the discovery when called upon by argparse in main()

    :param args:
    :param configinstance:
    :param logger:
    :return:
    """
    configinstance.load_yaml_file(args.config)
    config = configinstance.load()

    if not args.datatype:
        logging.error(
            "\n"
            "You must provide a datatype with the --datatype or -t option.\n\n"
            "Datatypes are found in your yaml config under\n "
            "testSet->testTitle->testElements->datatype \n\n"
            "Available types detected in config:\n  %s " % configinstance.get_datatypes_list())
        sys.exit(1)

    discovery_dict = {}
    discovery_dict['data'] = []

    for testSet in config['checks']:
        checkname = testSet['key']

        uri = testSet['data']['uri']

        for element in testSet['data']['testElements']:  # For every test element
            datatypes = element['datatype'].split(',')
            for datatype in datatypes:  # For each datatype found in testElements
                if datatype == args.datatype:  # Only add if datatype is interesting
                    # Add more useful properties to the discovery element
                    element = element.copy()
                    element.update(
                        {'datatype': datatype, 'checkname': checkname, 'resource_uri': uri})

                    # Apply Zabbix low level discovery formating to key names
                    #  (shift to uppercase)
                    for old_key in element.keys():
                        new_key = "{#" + old_key.upper() + "}"
                        element[new_key] = element.pop(old_key)

                    # Add this test element to the discovery dict.
                    logger.debug('Item discovered ' + str(element))
                    discovery_dict['data'].append(element)
    # Print discovery dict.
    print(json.dumps(discovery_dict, indent=3))


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


def main(arguements=None):
    """
    Program entry point.

    python url_monitor/main.py -c "customerAdminAPI_collectionStatusJobTotals" -k "jobSuccess"

    :param arguements:
    :return:
    """
    try:
        if arguements is None:  # __name__=__main__
            arguements = sys.argv[1:]
            progname = sys.argv[0]
        else:  # module entry
            arguements = arguements[1:]
            progname = arguements[0]
    except IndexError:
        print(return_epilog() + "\n")
        logging.error("Invalid options. Use --help for more information.")
        sys.exit(1)

    arg_parser = argparse.ArgumentParser(
        prog=progname,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=descriptionmacro,
        epilog=return_epilog())
    arg_parser.add_argument('COMMAND')
    arg_parser.add_argument(
        "-V",
        "--version",
        action='version',
        version='UNSUPPORTED OPTION'
    )
    arg_parser.add_argument(
        "--key",
        "-k",
        nargs='?',
        default=None,
        help="Optional with `check` command. Can be used to run checks on a limited"
             + " subset of item headings under testSet from the yaml config."
    )
    arg_parser.add_argument(
        "--datatype",
        "-t",
        nargs='?',
        default=None,
        help="Required with `discover` command. This filters objects from the config "
             + "that have a particular datatype. This data is used by low level discovery"
             + " in Zabbix.")
    arg_parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="Specify custom config file, system default /etc/url_monitor.yaml")
    arg_parser.add_argument(
        "--loglevel",
        default=None,
        help="Specify custom loglevel override. Available options [debug, info,"
             + " warn, critical, error, exceptions]")
    args = arg_parser.parse_args(args=arguements)

    configinstance = configuration.ConfigObject()
    configinstance.load_yaml_file(args.config)
    logger = configinstance.get_logger(args.loglevel)

    configinstance.pre_flight_check()
    config = configinstance.load()

    if args.COMMAND == "check":
        failed_exits = []
        for testSet in config['checks']:
            try:  # Catch all exceptions
                if args.key != None:
                    if testSet['key'] == args.key:
                        exit_val = check(testSet, configinstance, logger)
                        if exit_val != 0:
                            failed_exits.append(testSet['key'])
                else:
                    exit_val = check(testSet, configinstance, logger)

                    if exit_val != 0:
                        failed_exits.append(testSet['key'])
            except Exception as e:
                logger.exception(e)
        if len(failed_exits) > 0:
            logger.debug("{0} checks have failed".format(
                str(len(failed_exits))
            ))
            print("1")
        else:
            print("0")
    elif args.COMMAND == "discover":
        discover(args, configinstance, logger)


if __name__ == "__main__":
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    pid = os.fork()
    if pid > 0:
        # exit first parent
        sys.exit(0)

    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # do second fork
    pid = os.fork()
    if pid > 0:
        # exit from second parent, print eventual PID before
        print("Daemon PID %d" % pid)
        sys.exit(0)

    # start the daemon main loop
    entry_point()
