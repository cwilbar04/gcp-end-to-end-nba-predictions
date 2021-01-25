#!/usr/bin/env python
## Base CLI originally copied and modified from https://github.com/noahgift/myrepo/blob/master/cli.py


"""
Commandline tool for interacting with library
"""

import click

from mylibrary import __version__


@click.version_option(__version__)

@click.group()
@click.version_option(__version__)
def cli():
    """Github Machine Learning Tool
    """

if __name__ == '__main__':
    cli()
