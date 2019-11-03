from setuptools import setup

setup(
    name='mechanical_testing',
    version='0.0.0',
    author='Lucas Guesser Targino da Silva',
    author_email='lucasguesserts@gmail.com',
    description='A set of tools for processing mechanical testing data.',
	keywords='mechanical testing',
    packages=['mechanical_testing'],
    zip_safe=False,
    install_requires=[
        'pytest',
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
        'sphinx',
    ]
)