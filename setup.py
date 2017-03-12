"""Setup
"""
import os
from setuptools import setup, find_packages


setup (
    name='skyscan',
    version='0.1dev',
    author = "Adam Groszer",
    author_email = "agroszer@gmail.com",
    description = "Scan the sky",
    long_description='',
    license = "Proprietary",
    keywords = "",
    classifiers = [],
    packages = find_packages('src'),
    package_dir = {'':'src'},
    extras_require = dict(),
    install_requires = [
        'setuptools',
        'requests',
        'fire',
        'skyscanner',
        'pygsheets',
        'komodo-python-dbgp',
    ],
    include_package_data = True,
    zip_safe = False,
    entry_points = '''
    [console_scripts]
    main = skyscan.main:main
    '''
    )
