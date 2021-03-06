import os
import re
import sys
import subprocess
from setuptools import (
    setup,
    find_packages,
    Command,
)


class ApiDocs(Command):
    """
    A custom command that calls sphinx-apidoc
    see: https://www.sphinx-doc.org/en/latest/man/sphinx-apidoc.html
    """
    description = 'builds the api documentation using sphinx-apidoc'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = [
            None,  # in Sphinx < 1.7.0 the first command-line argument was parsed, in 1.7.0 it became argv[1:]
            '--force',  # overwrite existing files
            '--module-first',  # put module documentation before submodule documentation
            '--separate',  # put documentation for each module on its own page
            '-o', './docs/_autosummary',  # where to save the output files
            'msl',  # the path to the Python package to document
        ]

        import sphinx
        if sphinx.version_info[:2] < (1, 7):
            from sphinx.apidoc import main
        else:
            from sphinx.ext.apidoc import main  # Sphinx also changed the location of apidoc.main
            command.pop(0)

        main(command)
        sys.exit(0)


class BuildDocs(Command):
    """
    A custom command that calls sphinx-build
    see: https://www.sphinx-doc.org/en/latest/man/sphinx-build.html
    """
    description = 'builds the documentation using sphinx-build'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sphinx

        command = [
            None,  # in Sphinx < 1.7.0 the first command-line argument was parsed, in 1.7.0 it became argv[1:]
            '-b', 'html',  # the builder to use, e.g., create a HTML version of the documentation
            '-a',  # generate output for all files
            '-E',  # ignore cached files, forces to re-read all source files from disk
            'docs',  # the source directory where the documentation files are located
            './docs/_build/html',  # where to save the output files
        ]

        if sphinx.version_info[:2] < (1, 7):
            from sphinx import build_main
        else:
            from sphinx.cmd.build import build_main  # Sphinx also changed the location of build_main
            command.pop(0)

        build_main(command)
        sys.exit(0)


def read(filename):
    with open(filename) as fp:
        return fp.read()


def fetch_init(key):
    # open the __init__.py file to determine the value instead of importing the package to get the value
    init_text = read('msl/equipment/__init__.py')
    return re.search(r'{}\s*=\s*(.*)'.format(key), init_text).group(1).strip('\'\"')


def get_version():
    init_version = fetch_init('__version__')
    if 'dev' not in init_version:
        return init_version

    if 'develop' in sys.argv or ('egg_info' in sys.argv and '--egg-base' not in sys.argv):
        # then installing in editable (develop) mode
        #   python setup.py develop
        #   pip install -e .
        suffix = 'editable'
    else:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            # write all error messages from git to devnull
            with open(os.devnull, 'w') as devnull:
                out = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=file_dir, stderr=devnull)
        except:
            try:
                git_dir = os.path.join(file_dir, '.git')
                with open(os.path.join(git_dir, 'HEAD'), mode='rt') as fp1:
                    line = fp1.readline().strip()
                    if line.startswith('ref:'):
                        _, ref_path = line.split()
                        with open(os.path.join(git_dir, ref_path), mode='rt') as fp2:
                            sha1 = fp2.readline().strip()
                    else:  # detached HEAD
                        sha1 = line
            except:
                return init_version
        else:
            sha1 = out.strip().decode('ascii')

        suffix = sha1[:7]

    if init_version.endswith(suffix):
        return init_version

    # following PEP-440, the local version identifier starts with '+'
    return init_version + '+' + suffix


testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

install_requires = [
    'msl-loadlib',
    'msl-io @ https://github.com/MSLNZ/msl-io/archive/master.tar.gz',
    'pyserial>=3.0',
    'python-dateutil',
    'enum34;python_version<"3.4"',
]

tests_require = ['pytest-cov', 'nidaqmx']
if not testing:
    install_requires.append('numpy')
else:
    if sys.version_info[:2] == (2, 7):
        tests_require.extend(['zipp<2.0', 'pyparsing<3.0', 'pytest~=4.6', 'numpy<1.17', 'pyvisa<1.11', 'pyvisa-py<0.5'])
    elif sys.version_info[:2] == (3, 5):
        tests_require.extend(['pytest', 'numpy<1.19', 'pyvisa<1.11', 'pyvisa-py<0.5'])
    else:
        tests_require.extend(['pytest', 'numpy', 'pyvisa', 'pyvisa-py'])

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = ['sphinx', 'sphinx_rtd_theme'] + install_requires if needs_sphinx else []

version = get_version()

setup(
    name='msl-equipment',
    version=version,
    author=fetch_init('__author__'),
    author_email='info@measurement.govt.nz',
    url='https://github.com/MSLNZ/msl-equipment',
    description='Manage and communicate with equipment in the laboratory',
    long_description=read('README.rst'),
    platforms='any',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
    ],
    setup_requires=sphinx + pytest_runner,
    tests_require=tests_require,
    install_requires=install_requires,
    cmdclass={'docs': BuildDocs, 'apidocs': ApiDocs},
    packages=find_packages(include=('msl*',)),
    include_package_data=True,
)

if 'dev' in version and not version.endswith('editable'):
    # ensure that the value of __version__ is correct if installing the package from an unreleased code base
    init_path = ''
    if sys.argv[0] == 'setup.py' and 'install' in sys.argv and not {'--help', '-h'}.intersection(sys.argv):
        # python setup.py install
        try:
            cmd = [sys.executable, '-c', 'import msl.equipment as p; print(p.__file__)']
            output = subprocess.check_output(cmd, cwd=os.path.dirname(sys.executable))
            init_path = output.strip().decode()
        except:
            pass
    elif 'egg_info' in sys.argv:
        # pip install
        init_path = os.path.dirname(sys.argv[0]) + '/msl/equipment/__init__.py'

    if init_path and os.path.isfile(init_path):
        with open(init_path, mode='r+') as fp:
            source = fp.read()
            fp.seek(0)
            fp.write(re.sub(r'__version__\s*=.*', "__version__ = '{}'".format(version), source))
