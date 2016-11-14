# -*- coding: utf-8 -*-
# !/usr/bin/python

import sys

from setuptools import setup

sys.path.insert(0, '.')

if __name__ == "__main__":
    package = "url_monitor"
    setup(
        name=package,
        version="3.0.4",
        author="Rackspace Inc",
        author_email="jon.kelley@rackspace.com",
        url="https://github.com/rackerlabs/zabbix_url_monitor",
        license="ASLv2",
        packages=[package],
        package_dir={package: package},
        description=(
            'A zabbix plugin to perform URL endpoint monitoring for JSON and XML REST '
            'APIs, supporting multiple http auth mechinisms'
        ),
        long_description=(
            'A Zabbix plugin written in Python that creates low level discovery items '
            'containing values from your JSON API. It supports multiple requests auth '
            'backends including oauth, basicauth, and your even own custom requests '
            'auth provider plugins. The low level discovery items can generate item '
            'prototypes which can be used to represent your data through this plugin.'
        ),
        classifiers=[
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: System :: Monitoring',
            'Topic :: System :: Networking :: Monitoring',
            'Topic :: System :: Systems Administration ',
        ],
        entry_points={
            'console_scripts': ['url_monitor = url_monitor.main:main'],
        },
        data_files=[('/etc', ['url_monitor.yaml'])],
        install_requires=[
            'requests',
            'requests-oauthlib',
            'oauthlib',
            'argparse',
            'facterpy'
        ]
    )
