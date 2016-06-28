#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import sys
import packaging
import commons
import json
import configuration
import zbxsend as event
from zbxsend import Metric
import logging
import textwrap
import requests

__doc__ = """Program entry point"""

def returnEpilog():
    """ Formats the eplig footer generated by help """
    author_strings = []
    for name, email in zip(packaging.authors, packaging.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    help_descr = textwrap.fill(packaging.long_description, 72, replace_whitespace=True)
    return """{project} {version}\n{headerline}\n{description}\n{footerline}\n{authors}\nURL: <{url}>""".format(
        headerline=str('=' * len(packaging.version + packaging.project + ' ')),
        footerline=str('-' * 72),
        description=help_descr,
        project=packaging.project,
        version=packaging.version,
        authors='\n'.join(author_strings),
        url=packaging.url)

def check(testSet,configinstance,logger):
    """ Perform the checks when called upon by argparse in main() """
    config = configinstance.load()
    webinstance = commons.WebCaller(logger)

    # Make a request and check a resource
    try:
        uri = testSet['data']['uri']
    except KeyError, err:
        # We're missing the uri aren't we?
        error = "\n\nError: Missing " + str(err) + " under testSet item "+ str(testSet['key']) +", check cannot run.\n1"
        raise Exception("KeyError: " + str(err) + str(error))
    try:
        response = webinstance.run(config, uri, verify=True, expected_http_status=str(
            testSet['data']['ok_http_code']), identity_provider=testSet['data']['identity_provider'])
    except KeyError, err:
        # We're missing ok code arent we?
        error = "\n\nError: Missing " + str(err) + " under testSet item "+ str(testSet['key']) + "\n" \
            + "If you don't know `ok_http_code: any` will cover most services.\n1"
        raise Exception("KeyError: " + str(err) + str(error))
    except requests.exceptions.RequestException as e:
        logging.error("Error: Requests exception " + str(e))
        return 1

    metrics = []
    # For each testElement do our path check.
    for element in testSet['data']['testElements']:
        try:
            datatypes = element['datatype'].split(',')
        except KeyError, err:
            logging.error("Error: Missing " + str(err) + " in config under testSet: testElements, check cannot run.")
            logging.error("Most elements are dynamically generated but this one is required.")
            logging.error("You can generate 1 or a comma seperated list of datatypes")
            return 1
        # We need to make a metric for each explicit data type
        # (string,int,count)
        for datatype in datatypes:
            try:
                path = commons.omnipath(response.content, testSet[
                    'data']['response_type'], element)
            except KeyError, err:
                # We're missing one of these two keys aren't we?
                logging.error("Error: Missing " + str(err) + " in config under testElement, check cannot run.")
                logging.error("This must be response_type: json.")
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
            except KeyError, err:
                logging.error("Error: Missing " + str(err) + " in config under testSet: testElements, check cannot run.")
                logging.error("Most elements are dynamically generated but this one is required.")
                return 1
            logging.debug(str(element['key']) + ": " +
                  str(element['request_response']))

            # Applies a key format from the configuration file, allowing custom zabbix keys 
            # for your items reporting to zabbix. Any element in testSet can be substituted,
            #  the {uri} and Pdatatype} are also made available.
            metrickey = config['config']['zabbix']['item_key_format'].format(**element)

            metrics.append(Metric('url_monitor',
                                  metrickey,
                                  element['request_response']))

    # Send metrics to zabbix
    logging.info('Preparing to send metrics: ' + str(metrics))
    logging.debug('Zabbix host ' +
                  str(config['config']['zabbix']['host']) + ' port ' + str(config['config']['zabbix']['port']))
    event.send_to_zabbix(metrics, config['config']['zabbix']['host'], config['config']['zabbix']['port'])
    return 0

def discover(args,configinstance,logger):
    """ Perform the discovery when called upon by argparse in main()"""
    configinstance.load_yaml_file(args.config)
    config = configinstance.load()

    if not args.datatype:
        logging.error("\nYou must provide a datatype with the --datatype or -t option.\n\n" \
              + "Datatypes are found in your yaml config under\n testSet->testTitle-" \
              + ">testElements->datatype \n\nAvailable types detected in config:" \
              + "\n  %s " % configinstance.getDatatypesList())
        sys.exit(1)

    discoveryDict = {}
    discoveryDict['data'] = []

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
                    discoveryDict['data'].append(element)
    # Print discovery dict.
    print(json.dumps(discoveryDict, indent=3))

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))

def main(arguements=None):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`

    python url_monitor/main.py -c "customerAdminAPI_collectionStatusJobTotals" -k "jobSuccess"
    
    """
    try:
        if arguements is None:  # __name__=__main__
            arguements = sys.argv[1:]
            progname = sys.argv[0]
        else: # module entry
            arguements = arguements[1:]
            progname = arguements[0]
    except IndexError:
        print(returnEpilog() + "\n")
        logging.error("Invalid options. Use --help for more information.")
        sys.exit(1)

    arg_parser = argparse.ArgumentParser(
        prog=progname,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=packaging.description,
        epilog=returnEpilog())
    arg_parser.add_argument('COMMAND')
    arg_parser.add_argument(
        "-V",
        "--version",
        action='version',
        version='{0} {1}'.format(packaging.project, packaging.version))
    arg_parser.add_argument(
        "--key",
        "-k",
        nargs='?',
        default=None,
        help="Optional with `check` command. Can be used to run checks on a limited" \
            + " subset of item headings under testSet from the yaml config."
    )
    arg_parser.add_argument(
        "--datatype",
        "-t",
        nargs='?',
        default=None,
        help="Required with `discover` command. This filters objects from the config " \
           + "that have a particular datatype. This data is used by low level discovery" \
           + " in Zabbix.")
    arg_parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="Specify custom config file, system default /etc/url_monitor.yaml")
    arg_parser.add_argument(
        "--loglevel",
        default=None,
        help="Specify custom loglevel override. Available options [debug, info," \
           + " warn, critical, error, exceptions]")
    args = arg_parser.parse_args(args=arguements)

    configinstance = configuration.ConfigObject()
    configinstance.load_yaml_file(args.config)
    configinstance.preFlight()
    config = configinstance.load()
    logger = logging.getLogger(packaging.package)
    args.loglevel = configinstance.get_log_level(args.loglevel)
    logging.basicConfig(level=args.loglevel)
    if args.COMMAND == "check":
        failed_exits = []
        for testSet in config['checks']:
            if args.key != None:
                if testSet['key'] == args.key:
                    exit_val = check(testSet,configinstance,logger)
                    if exit_val != 0:
                        failed_exits.append(testSet['key'])
            else:
                exit_val = check(testSet,configinstance,logger)

                if exit_val != 0:
                    failed_exits.append(testSet['key'])
        if len(failed_exits) > 0:
            raise Exception(str(len(failed_exits)) + " checks have failed: " + str(failed_exits) + "\n1")
    elif args.COMMAND == "discover":
        discover(args,configinstance,logger)

if __name__ == '__main__':
    entry_point()
