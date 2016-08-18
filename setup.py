#!/usr/bin/env python

############################################################################
# Copyright (c) 2015-2016 Saint Petersburg State University
# Copyright (c) 2011-2015 Saint Petersburg Academic University
# All Rights Reserved
# See file LICENSE for details.
############################################################################

import glob
import os
import subprocess
import sys
from os.path import join, isfile, abspath, dirname, relpath, isdir

import shutil
from setuptools import setup, find_packages

from libs import qconfig
from libs.log import get_logger
logger = get_logger(qconfig.LOGGER_DEFAULT_NAME)
logger.set_up_console_handler(debug=True)

from libs.search_references_meta import download_blast_files, download_all_blast_files
from libs.glimmer import compile_glimmer
from libs.gage import compile_gage
from libs.ca_utils.misc import compile_aligner
from libs.ra_utils import compile_reads_analyzer_tools

name = 'quast'
quast_package = 'libs'


if abspath(dirname(__file__)) != abspath(os.getcwd()):
    logger.error('Please, change to ' + dirname(__file__) + ' before running setup.py')
    sys.exit()


if sys.argv[-1] == 'clean':
    logger.info('Cleaning up binary files...')
    compile_aligner(logger, only_clean=True)
    compile_reads_analyzer_tools(logger, only_clean=True)
    download_all_blast_files(logger, only_clean=True)
    compile_glimmer(only_clean=True)
    compile_gage(only_clean=True)
    if isdir('build'):
        shutil.rmtree('build')
    if isdir('dist'):
        shutil.rmtree('dist')
    if isdir(name + '.egg-info'):
        shutil.rmtree(name + '.egg-info')
    logger.info('Done.')
    sys.exit()


def write_version_py():
    version_py = os.path.join(os.path.dirname(__file__), quast_package, 'version.py')

    with open('VERSION.txt') as f:
        v = f.read().strip().split('\n')[0]
    try:
        import subprocess
        git_revision = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).rstrip()
    except:
        git_revision = ''
        pass
    with open(version_py, 'w') as f:
        f.write((
            '# Do not edit this file, pipeline versioning is governed by git tags\n' +
            '__version__ = \'' + v + '\'\n' +
            '__git_revision__ = \'' + git_revision + '\''))
    return v

version = write_version_py()


if sys.argv[-1] == 'tag':
    cmdl = 'git tag -a %s -m "Version %s" && git push --tags' % (version, version)
    os.system(cmdl)
    sys.exit()


if sys.argv[-1] == 'publish':
    # not working for now; need to correctly make sdist using source files only
    cmdl = 'python setup.py sdist upload'
    os.system(cmdl)
    sys.exit()


logger.info("""------------------------------------------
 Installing QUAST version {}
------------------------------------------
""".format(version))


if sys.argv[-1] in ['install', 'develop', 'build', 'build_ext']:
    logger.info('* Compiling aligner *')
    compile_aligner(logger)
    logger.info('* Compiling read analisis tools *')
    compile_reads_analyzer_tools(logger)
    logger.info('* Compiling Blast *')
    download_all_blast_files(logger)
    logger.info('* Compiling Glimmer *')
    compile_glimmer()
    logger.info('* Compiling GAGE *')
    compile_gage()
    logger.info('')


def find_package_files(dirpath, package=quast_package):
    paths = []
    for (path, dirs, fnames) in os.walk(join(package, dirpath)):
        for fname in fnames:
            fpath = join(path, fname)
            paths.append(relpath(fpath, package))
    return paths


if qconfig.platform_name == 'macosx':
    nucmer_files = find_package_files('E-MEM-osx')
    sambamba_files = [join('sambamba', 'sambamba_osx')]
else:
    nucmer_files = find_package_files('MUMmer3.23-linux') + find_package_files('E-MEM-linux')
    sambamba_files = [join('sambamba', 'sambamba_linux')]

bwa_files = [
    join('bwa', fp) for fp in os.listdir(join(quast_package, 'bwa'))
    if isfile(join(quast_package, 'bwa', fp)) and fp.startswith('bwa')]

setup(
    name=name,
    version=version,
    author='Alexei Gurevich',
    author_email='alexeigurevich@gmail.com',
    description="Genome assembly evaluation toolkit",
    long_description=__doc__,
    keywords=['bioinformatics', 'genome assembly', 'metagenome assembly', 'visualization'],
    url='quast.sf.net',
    license='GPLv2',

    packages=find_packages(),
    package_data={
        quast_package:
            find_package_files('html_saver') +
            nucmer_files +
            bwa_files +
            find_package_files('manta') +
            ['bedtools/bin/*'] +
            sambamba_files +
            find_package_files('genemark/' + qconfig.platform_name) +
            find_package_files('genemark-es/' + qconfig.platform_name) +
            find_package_files('genemark-es/lib') +
            find_package_files('glimmer') +
            find_package_files('blast') +
            find_package_files('gage')
    },
    include_package_data=True,
    zip_safe=False,
    scripts=['quast.py', 'metaquast.py', 'icarus.py'],
    data_files=[
        ('', [
            'README.txt',
            'CHANGES.txt',
            'VERSION.txt',
            'LICENSE.txt',
            'manual.html',
        ]),
        ('test_data', find_package_files('test_data', package='')),
        ('external_tools', [
            'external_tools/blast/' + qconfig.platform_name + '/blastn',
            'external_tools/blast/' + qconfig.platform_name + '/makeblastdb',
        ]),
    ],
    install_requires=[
        'matplotlib',
        'joblib',
        'simplejson',
    ],
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)

logger.info("""
--------------------------------
 QUAST installation complete!
--------------------------------
For help in running QUAST, please see the documentation available
at quast.bioinf.spbau.ru/manual.html or run: quast --help
""")
