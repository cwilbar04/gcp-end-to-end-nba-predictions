#!/usr/bin/env python
## Base CLI originally copied and modified from https://github.com/noahgift/myrepo/blob/master/cli.py


"""
Commandline tool for interacting with library
"""
#badcode=
import click

from myrepolib import __version__


@click.version_option(__version__)
