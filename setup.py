from setuptools import setup, find_packages

__version__ = '0.7'
description = 'Public Domain Calculators library and webapp.'

setup(
    name='pdcalc',
    version=__version__,
    description=description,
    long_description=description,
    license='MIT',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://publicdomaincalculators.okfn.org/',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    # package_data={'pdcalc': ['i18n/*/LC_MESSAGES/*.mo']},
    install_requires=[
        ],
    #message_extractors = {'pdcalc': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    """,
)
