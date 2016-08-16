#!/usr/bin/env python3

from setuptools import find_packages
from setuptools import setup

tests_require = [
    'pytest-cov',
    'pytest-flakes',
    'pytest-pep8',
    'pytest',  # Installed first if last item
]

setup(
    name='tochka-nasdaq',
    version='0.1.0',
    url='https://github.com/infotim/tochka-nasdaq',
    author='Timofey Stolbov',
    author_email='timofey@stolbov.info',
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'tochka_nasdaq': ['templates/*']},
    zip_safe=False,

    setup_requires=['pytest-runner'],
    tests_require=tests_require,

    install_requires=[
        'psycopg2', 'sqlalchemy', 'lxml', 'flask'
    ],
    extras_require={
        'dev': tests_require,
    },
    entry_points={
        'console_scripts': [
            'tochka-nasdaq-loader = tochka_nasdaq.load:main',
            'tochka-nasdaq-front = tochka_nasdaq.front:main',
        ],
    },
)
