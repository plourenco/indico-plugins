# This file is part of the Indico plugins.
# Copyright (C) 2002 - 2020 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

import errno
import os
import re
import sys
from collections import defaultdict

import click
import yaml
from packaging.version import Version


click.disable_unicode_literals_warning = True
START_MARKER = '# BEGIN GENERATED REQUIREMENTS'
END_MARKER = '# END GENERATED REQUIREMENTS'


def _find_plugins():
    subdirs = sorted(x for x in next(os.walk('.'))[1]
                     if x[0] != '.' and x != '_meta' and os.path.exists(os.path.join(x, 'setup.py')))
    for subdir in subdirs:
        path = os.path.join(subdir, 'setup.py')
        with open(path) as f:
            setup_py = f.read()
        # try:
        name = re.search(r'''name=(['"])(.+)\1''', setup_py)
        version = re.search(r'''version=(['"])(.+)\1''', setup_py)
        if name is None or version is None:
            click.secho(f'Could not extract name/version from {path}', fg='red', bold=True)
            continue
        minver = str(Version(version.group(2)))
        yield name.group(2), minver


def _get_config():
    rv = {'extras': {}, 'skip': []}
    try:
        f = open('_meta/meta.yaml')
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise
    else:
        with f:
            rv.update(yaml.safe_load(f))
    return rv


def _update_meta(data):
    path = '_meta/setup.py'
    with open(path) as f:
        content = f.read()
    new_content = re.sub(r'(?<={}\n).*(?=\n{})'.format(re.escape(START_MARKER), re.escape(END_MARKER)), data, content,
                         flags=re.DOTALL)
    if content == new_content:
        return False
    with open(path, 'w') as f:
        f.write(new_content)
    return True


@click.command()
@click.argument('nextver')
def cli(nextver):
    if not os.path.isdir('_meta/'):
        click.secho('Could not find meta package (_meta subdir)', fg='red', bold=True)
        sys.exit(1)

    nextver = Version(nextver)
    if nextver.dev is None:
        nextver = Version(str(nextver) + '-dev')

    config = _get_config()
    plugins_require = []
    extras_require = defaultdict(list)
    for name, minver in sorted(_find_plugins()):
        if name in config['skip']:
            continue
        pkgspec = f'{name}>={minver},<{nextver}'
        if name in config['extras']:
            extras_require[config['extras'][name]].append(pkgspec)
        else:
            plugins_require.append(pkgspec)

    output = []
    if not plugins_require:
        output.append('plugins_require = []')
    else:
        output.append('plugins_require = [')
        for entry in plugins_require:
            output.append('    {!r},'.format(str(entry)))
        output.append(']')
    if not extras_require:
        output.append('extras_require = {}')
    else:
        output.append('extras_require = {')
        for extra, pkgspecs in sorted(extras_require.items()):
            output.append('    {!r}: {!r},'.format(extra, list(map(str, sorted(pkgspecs)))))
        output.append('}')

    if _update_meta('\n'.join(output)):
        click.secho('Updated meta package', fg='green')
    else:
        click.secho('Meta package already up to date', fg='yellow')


if __name__ == '__main__':
    cli()
