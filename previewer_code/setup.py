# This file is part of the Indico plugins.
# Copyright (C) 2002 - 2020 CERN
#
# The Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License;
# see the LICENSE file for more details.

from setuptools import find_packages, setup


setup(
    name='indico-plugin-previewer-code',
    version='3.0-dev',
    description='Syntax highlighter for code attachments in Indico',
    url='https://github.com/indico/indico-plugins',
    license='MIT',
    author='Indico Team',
    author_email='indico-team@cern.ch',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'indico>=3.0.dev0',
        'Pygments>=2.7.2,<3',
    ],
    python_requires='~=3.9',
    entry_points={'indico.plugins': {'previewer_code = indico_previewer_code:CodePreviewerPlugin'}}
)
