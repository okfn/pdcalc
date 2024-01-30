from setuptools import setup, find_packages
from pd import __version__, __author__

setup(
    name = 'pd',
    version = __version__,
    packages = find_packages(),
    install_requires = open('./requirements.txt').readlines(),
    # metadata for upload to PyPI
    author = __author__.split("<")[0].strip(),
    author_email = __author__.split("<")[1].split(">")[0].strip(),
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
    entry_points={
        'console_scripts': [
            'pdcalc = pd.pdcalc:pdcalc',
        ],
    }
)

