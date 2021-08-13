'''
Everything to package ENACrestic

Based on :
+ https://packaging.python.org/tutorials/packaging-projects/
+ https://github.com/pypa/sampleproject

Build it with :
$ python3 -m build
'''

from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

VERSION='is set by `exec` command here bellow'
exec((here / 'src/enacrestic/const.py').read_text(encoding='utf-8'))

setup(
    name='ENACrestic',
    version=VERSION,
    description='Automate backups using restic',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/EPFL-ENAC/ENACrestic',
    author='Samuel Bancal',
    author_email='Samuel.Bancal@epfl.ch',

    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Archiving :: Backup',
    ],

    keywords='backup, restic',

    package_dir={'': 'src'},

    packages=['enacrestic'],

    python_requires='>=3.6, <4',

    install_requires=[
        'PyQt5',
        'python-pidfile',
    ],

    extras_require={
        'dev': [],
        'test': [],
    },

    package_data={
        'enacrestic': ['pixmaps/*.png'],
    },

    data_files=[
        ('share/applications', ['enacrestic.desktop']),
        ('share/icons', ['enacrestic.png']),
    ],

    entry_points={
        'console_scripts': [
            'enacrestic=enacrestic:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/EPFL-ENAC/ENACrestic/issues',
        'Source': 'https://github.com/EPFL-ENAC/ENACrestic/',
    },
)
