from setuptools import setup, find_packages
from pd import __version__

setup(
    name = 'pdw2',
    version = __version__,
    packages = find_packages(),
    install_requires = open('./requirements.txt').readlines(),
    # metadata for upload to PyPI
    author = 'Open Knowledge Foundation',
    author_email = 'info@okfn.org',
    description = 'PublicDomainWorks.net web app and API.',
    license = 'MIT',
    url = 'http://publicdomain.okfn.org/',
    download_url = 'http://bitbucket.org/okfn/pdw2',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

