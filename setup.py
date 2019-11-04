""" Mechanical Testing enables auto analysing the data from mechanical tests.

Mechanical tests available:

- Tensile test

"""

from setuptools import setup

DOCLINES = (__doc__ or '').split("\n")

setup(
    # Metadata
    name='mechanical_testing',
    version='0.0.0-rc.1',
    url='https://github.com/lucasguesserts/mechanical_testing',
    download_url='https://pypi.python.org/pypi/mechanical-testing',
    author='Lucas Guesser Targino da Silva',
    author_email='lucasguesserts@gmail.com',
    classifiers=[
        'Intended Audience :: Education',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
    ],
    license='MIT',
    license_file='LICENSE.txt',
    description = DOCLINES[0],
    long_description = "\n".join(DOCLINES[2:]),
	keywords=[
        'mechanical testing',
        'engineering',
    ],
    project_urls={
        'Source Code': 'https://github.com/lucasguesserts/mechanical_testing',
        'Documentation': 'https://mechanical-testing.readthedocs.io/en/latest/',
        'Build': 'https://travis-ci.org/lucasguesserts/mechanical_testing',
        'Code Coverage': 'https://codecov.io/gh/lucasguesserts/mechanical_testing',
    },
    # Options
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
    ],
    tests_require=[
        'pytest',
    ],
    python_requires='>=3.0',
)