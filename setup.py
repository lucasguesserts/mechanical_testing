from setuptools import setup

setup(
    # Metadata
    name='mechanical_testing',
    version='0.0.0',
    url='https://github.com/lucasguesserts/mechanical_testing',
    download_url='https://github.com/lucasguesserts/mechanical_testing/archive/master.zip',
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
    description='A set of tools for processing mechanical testing data.',
    long_description='file: README.md',
	keywords=[
        'mechanical testing',
        'engineering',
    ],
    # Options
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
    ],
    tests_require=[
        'pytest',
    ]
)